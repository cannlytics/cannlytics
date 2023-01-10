/**
 * Webpack Module Bundler | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/9/2020
 * Updated: 3/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
const appName = 'console';
// const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const Dotenv = require('dotenv-webpack');
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = env => {
  return {
    mode: env.production ? 'production' : 'development',
    devtool: env.production ? 'source-map' : 'eval', // source-map required for minimization.
    devServer: {
      devMiddleware: {
      	writeToDisk: true, // Write files to disk in dev mode, so that Django can serve the assets.
      },
    },
    resolve: {
      extensions: ['.js'],
    },
    entry: {
      cannlytics: `./assets/js/index.js`,
    },
    output: {
      path: path.resolve(__dirname, `./static/${appName}`), // Should be in STATICFILES_DIRS.
      filename: './bundles/[name].min.js',
      library: 'cannlytics',
      libraryTarget: 'var',
      hotUpdateChunkFilename: './bundles/hot/hot-update.js',
      hotUpdateMainFilename: './bundles/hot/hot-update.json',
    },
    module: {
      rules: [

        // Compiles SCSS to CSS.
        {
          test: /\.(scss)$/,
          use: [
            {
              // Inject CSS to page by creating `style` nodes from JS strings.
              loader: 'style-loader',
            },
            {
              // Translate CSS into CommonJS modules.
              loader: 'css-loader',
            },
            {
              // Run post compile actions.
              loader: 'postcss-loader',
              options: {
                postcssOptions: {
                  plugins: function () {
                    return [
                      require('precss'),
                      require('autoprefixer')
                    ];
                  }
                },
              },
            },
            {
              // Compile Sass to CSS.
              loader: 'sass-loader',
            }
          ]
        },

        // Convert ES2015 to JavaScript.
        {
          test: /\.js$/,
          exclude: '/node_modules/',
          loader: 'babel-loader',
          options: {
            compact: true,
          },
        },

      ],
    },

    // Minimize JavaScript in production.
    optimization: {
      minimize: env.production,
      minimizer: [
        new TerserPlugin({ parallel: true }),
        // new CssMinimizerPlugin({}),
      ],
    },
    
    // Define maximum optimal bundle-size.
    performance: {
      maxEntrypointSize: 512000 * 4,
      maxAssetSize: 512000 * 4,
    },

    // Useful plugins.
    plugins: [

      // Make .env variables available in the entry file.
      // WARNING: Any variables used in JavaScript will be compiled.
      new Dotenv({ path: '../.env' }),

    ],

  }
}
