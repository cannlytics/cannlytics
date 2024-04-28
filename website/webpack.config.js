/**
 * Webpack Module Bundler | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 1/5/2021
 * Updated: 7/30/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
*/
const appName = 'website';
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
      hot: false, // Note: This is problematic.
      liveReload: false,
    },
    resolve: {
      extensions: ['.js'],
    },
    entry: [
      './assets/css/cannlytics.scss',
      './assets/js/index.js',
      // You can add additional JS here.
    ],
    // entry: {
    //   cannlytics: `./assets/js/index.js`,
    // },
    output: {
      path: path.resolve(__dirname, `./static/${appName}`),
      filename: './js/bundles/cannlytics.min.js',
      library: 'cannlytics', // Turns JavaScript into a module.
      libraryTarget: 'var',
      hotUpdateChunkFilename: './js/bundles/hot/hot-update.js',
      hotUpdateMainFilename: './js/bundles/hot/hot-update.json'
    },
    module: {
      rules: [

        // Compiles SCSS to CSS.
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
                      // require('precss'),
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
};
