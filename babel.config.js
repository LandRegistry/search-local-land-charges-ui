module.exports = {
  presets: [
    [
      require('@babel/preset-env').default,
      {
        useBuiltIns: 'usage',
        corejs: 3,
      },
    ],
  ],
};
