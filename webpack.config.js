const glob = require('glob');
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleAnalyzerPlugin =
  require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const fs = require('fs');
const yaml = require('js-yaml');
const webpack = require("webpack");
const TerserPlugin = require("terser-webpack-plugin");


// Workaround for https://github.com/webpack/webpack/issues/7300 whereby
// webpack outputs empty chunks when used with the css extract plugin
// See exact solution at https://github.com/webpack/webpack/issues/7300#issuecomment-413959996
// Without this workaround, the css extract solution leaves behind empty JavaScript files
// Once this ticket has been resolved this workaround can be removed
class MiniCssExtractPluginCleanUp {
  constructor(deleteWhere = /css.*\.js(\.map)?$/) {
    this.shouldDelete = new RegExp(deleteWhere);
  }
  apply(compiler) {
    compiler.hooks.emit.tapAsync(
      'MiniCssExtractPluginCleanup',
      (compilation, callback) => {
        Object.keys(compilation.assets).forEach((asset) => {
          if (this.shouldDelete.test(asset)) {
            delete compilation.assets[asset];
          }
        });
        callback();
      }
    );
  }
}

// Grab the appropriate port to use for the websockets by parsing the docker compose fragment
const dockerComposeFragment = yaml.load(
  fs.readFileSync('fragments/docker-compose-fragment.yml')
);
const applicationPort =
  dockerComposeFragment.services['search-local-land-charge-ui'].ports[0].split(':')[0];

// Collect top level js and scss entrypoints
const files = glob.sync(path.join('server/assets/src/{js,scss}/*.{js,scss}'));
const entrypoints = files.reduce((accumulator, value) => {
  const assetExtension = path.extname(value);
  const extMap = {
    '.scss': 'css',
    '.js': 'js',
  };

  accumulator[
    path.join(extMap[assetExtension], path.basename(value, assetExtension))
  ] = path.resolve(value);
  return accumulator;
}, {});

// Set up some dependancies to reduce JS file sizes
entrypoints['js/confirm-search-area'] = {
  import: entrypoints['js/confirm-search-area'],
  dependOn: 'js/mapping'
}
entrypoints['js/define-search-area'] = {
  import: entrypoints['js/define-search-area'],
  dependOn: 'js/mapping'
}
entrypoints['js/mapping'] = {
  import: entrypoints['js/mapping'],
  dependOn: ['js/proj4', 'js/jquery']
}
// Add separate jquery and proj4 files since we import all of them anyway
// We can import only the needed parts of Openlayers though so not included
entrypoints['js/jquery'] = 'jquery'
entrypoints['js/proj4'] = 'proj4'

// Construct the webpack config
const webpackConfig = {
  mode: 'production',
  bail: false,
  devtool: 'source-map',
  output: {
    path: path.resolve('server/assets/dist'),
  },
  resolve: {
    modules: ['node_modules'],
  },
  resolveLoader: {
    modules: ['node_modules'],
  },
  stats: {
    assets: true,
    colors: true,
    entrypoints: false,
    hash: false,
    modules: false,
    version: false,
  },
  entry: entrypoints,
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules\/(?!(govuk-react-components|hmlr-frontend)\/).*/,
        use: [
          {
            loader: 'babel-loader',
          },
        ],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name(file) {
                const componentName = path.dirname(file).split(path.sep).pop();
                return `images/hmlr-frontend/${componentName}/[name].[ext]`;
              },
            },
          },
        ],
      },
      {
        test: /\.scss$/,
        resolve: {
          extensions: ['.scss'],
        },
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              url: false,
            },
          },
          {
            loader: 'postcss-loader',
          },
          {
            loader: 'sass-loader',
            options: {
              additionalData: '$hmlr-assets-path: "/ui/";',
              sassOptions: {
                quietDeps: true,
                includePaths: ['/supporting-files'],
              },
            },
          },
        ],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin(),
    new MiniCssExtractPluginCleanUp(),
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      reportFilename: '../../../bundle-report.html',
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    })
  ],
  // create singular runtime chunk to load all the bits
  optimization: {
    runtimeChunk: {
      name: 'js/runtime',
    },
    // changes to allow us to load modules from console/tests
    moduleIds: "named",
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          keep_fnames: true,
        }
      }),
    ]
  },
};

// If we're running inside the docker container, node_modules is placed
// at a different location defined by the NODE_PATH environment variable
// so we need to tell webpack to check there too
if ('NODE_PATH' in process.env) {
  webpackConfig.resolve.modules.push(process.env.NODE_PATH);
  webpackConfig.resolveLoader.modules.push(process.env.NODE_PATH);
}

module.exports = webpackConfig;
