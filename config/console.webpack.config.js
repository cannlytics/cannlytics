/**
 * Webpack Module Bundler | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/9/2020
 * Updated: 3/13/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
const appName = 'console';
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
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
      cannlytics: `../${appName}/assets/js/index.js`,
    },
    output: {
      path: `../${appName}/static/${appName}`, // Should be in STATICFILES_DIRS.
      filename: './bundles/[name].min.js',
      library: { // Turns JavaScript into a module.
        name: 'cannlytics',
        type: 'umd',
      },
      libraryTarget: 'var',
      hotUpdateChunkFilename: './bundles/hot/hot-update.js',
      hotUpdateMainFilename: './bundles/hot/hot-update.json',
    },
    module: {
      rules: [

        // Compiles SCSS to CSS.
        {
          test: /\.(scss)$/,
          use: [{
            loader: 'style-loader', // Inject CSS to page by creating `style` nodes from JS strings.
          }, {
            loader: 'css-loader', // Translate CSS into CommonJS modules.
          }, {
            loader: 'postcss-loader', // Run post compile actions.
            options: {
              postcssOptions: {
                plugins: function () { // Use post css plugins, can be exported to postcss.config.js
                  return [
                    require('precss'),
                    require('autoprefixer')
                  ];
                }
              },
            },
          }, {
            loader: 'sass-loader' // Compile Sass to CSS.
          }]
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
        new CssMinimizerPlugin({}),
      ],
    },

    // Useful plugins.
    plugins: [

      // Make .env variables available in the entry file.
      // WARNING: Any variables used in JavaScript will be compiled.
      new Dotenv(),

    ],

  }
}
