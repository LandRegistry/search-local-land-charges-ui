const config = require('../config');
const path = require('path');
const util = require('util');
const copy = util.promisify(require('copy'));

module.exports = async () => {
  // 1. Copy images from govuk-frontend
  const govukTemplatePath = path.dirname(require.resolve('govuk-frontend'));
  await copy(
    path.join(govukTemplatePath, 'assets/**/*.*'),
    config.destinationPath
  );

  // 2. Copy images from hmlr-frontend, overwriting any identical ones from govuk-frontend
  const patternLibraryPath = path.dirname(require.resolve('@hmlr/frontend'));
  await copy(
    path.join(patternLibraryPath, 'assets/**/*.{png,jpg,svg}'),
    config.destinationPath
  );

  // 3. Copy application images, overwriting anything generic from the two frontend packages
  await copy(
    path.join(config.sourcePath, 'images/**'),
    path.join(config.destinationPath, 'images')
  );
};
