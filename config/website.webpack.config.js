/**
 * Webpack Module Bundler | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/5/2021
 * Updated: 1/1/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
*/
const appName = 'website';
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
      }
    },
    resolve: {
      extensions: ['.js'],
    },
    entry: [
      `./${appName}/assets/css/cannlytics.scss`,
      `./${appName}/assets/js/index.js`,
      // You can add additional JS here.
    ],
    output: {
      path: path.resolve(__dirname, `${appName}/static/${appName}`),
      filename: './js/bundles/cannlytics.min.js',
      libraryTarget: 'var',
      library: 'cannlytics', // Turns JavaScript into a module.
      hotUpdateChunkFilename: './js/bundles/hot/hot-update.js',
      hotUpdateMainFilename: './js/bundles/hot/hot-update.json'
    },
    module: {
      rules: [
        {
          test: /\.s[ac]ss$/i,
          use: [
            {
              // Inject CSS to page by creating `style` nodes from JS strings.
              loader: 'style-loader'
            },
            {
              // Translate CSS into CommonJS modules.
              loader: 'css-loader'
            },
            {
              // Run postcss actions.
              loader: 'postcss-loader',
              options: {
                postcssOptions: {
                  plugins: function () {
                    return [
                      require('autoprefixer')
                    ];
                  }
                }
              }
            },
            {
              // Compiles Sass to CSS.
              loader: 'sass-loader',
            },
          ],
        },
        {
          // Convert ES2015 to JavaScript.
          test: /\.js$/,
          exclude: '/node_modules/',
          loader: 'babel-loader',
          options: {
            compact: true,
          },
        },
      ],
    },
    optimization: {
      minimize: env.production, // Minimize JavaScript in production.
      minimizer: [new TerserPlugin({ parallel: true })],
    },
    plugins: [
      new Dotenv(), // Make .env variables available in entry file.
    ],
  }
};
