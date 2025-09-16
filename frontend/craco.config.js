const { when, whenDev } = require('@craco/craco');

module.exports = {
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      // Suppress deprecation warnings in development
      if (env === 'development') {
        // Override the deprecated webpack dev server options
        if (webpackConfig.devServer) {
          // Remove deprecated options and use the new setupMiddlewares
          delete webpackConfig.devServer.onBeforeSetupMiddleware;
          delete webpackConfig.devServer.onAfterSetupMiddleware;
          
          // Use the new setupMiddlewares option
          webpackConfig.devServer.setupMiddlewares = (middlewares, devServer) => {
            // Add any custom middleware here if needed
            return middlewares;
          };
        }
        
        // Suppress specific deprecation warnings
        webpackConfig.ignoreWarnings = [
          /DEP_WEBPACK_DEV_SERVER_ON_AFTER_SETUP_MIDDLEWARE/,
          /DEP_WEBPACK_DEV_SERVER_ON_BEFORE_SETUP_MIDDLEWARE/,
          /DEP0060/
        ];
        
        // Add plugin to suppress warnings
        if (!webpackConfig.plugins) {
          webpackConfig.plugins = [];
        }
        
        // Suppress node warnings
        webpackConfig.plugins.push(
          new (require('webpack')).DefinePlugin({
            'process.env.NODE_NO_WARNINGS': JSON.stringify('1')
          })
        );
      }
      
      return webpackConfig;
    }
  },
  devServer: whenDev(() => ({
    // Modern webpack dev server configuration
    setupMiddlewares: (middlewares, devServer) => {
      // Custom middleware setup if needed
      return middlewares;
    },
    // Explicitly remove deprecated options
    onBeforeSetupMiddleware: undefined,
    onAfterSetupMiddleware: undefined,
    // Suppress dev server messages
    client: {
      logging: 'warn'
    }
  }))
};
