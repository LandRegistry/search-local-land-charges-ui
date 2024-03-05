const copyImages = require('./tasks/images');

let start = new Date().getTime();

(async () => {
  try {
    await copyImages();
  } catch (e) {
    console.error(e);
    process.exit(1);
  }

  let end = new Date().getTime();
  console.log('Prebuild finished in ', end - start, ' ms');
})();
