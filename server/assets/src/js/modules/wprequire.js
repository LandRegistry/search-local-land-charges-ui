global.WPRequire = function(module) {
    for (let modName of Object.getOwnPropertyNames(__webpack_require__.m)) {
        if (modName.endsWith(module) || modName.endsWith(module + ".js")) {
            return __webpack_require__(modName);
        }
    }
}

global.WPFindFunction = function(module, functionName) {
    for (let func of Object.getOwnPropertyNames(module)) {
        if (module[func].name == functionName) {
            return module[func];
        }
    }
}




