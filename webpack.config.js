/**
 * Webpack | Cannlytics Console
 * Author: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/9/2020
 * Updated: 5/7/2021
 * Resources:
 *     https://pascalw.me/blog/2020/04/19/webpack-django.html
 *     https://medium.com/@poshakajay/heres-how-i-reduced-my-bundle-size-by-90-2e14c8a11c11
 *     https://webpack.js.org/guides/code-splitting/
 *     https://owais.lone.pw/blog/webpack-plus-reactjs-and-django/
 *     https://webpack.js.org/migrate/5/
 */

// Webpack plugins.
const BundleTracker = require('webpack-bundle-tracker')
const Dotenv = require('dotenv-webpack');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require("terser-webpack-plugin");

// Node utilities.
const exec = require('child_process').exec;
const nodeExternals = require('webpack-node-externals');
const path = require('path');
const appName = 'cannlytics_console';

module.exports = env => {
  return {
    mode: env.production ? 'production' : 'development',
    devtool: env.production ? 'source-map' : 'eval',
    devServer: {
      writeToDisk: true, // Write files to disk in dev mode, so that Django can serve the assets.
    },
    externals: [nodeExternals({
      allowlist: [/^chartjs/, /^chart.js/],
    })], // Ignore all modules in node_modules folder.
    entry: {
      cannlytics_css: `./${appName}/assets/css/cannlytics.scss`,
      console_css: `./${appName}/assets/css/console.scss`,
      cannlytics: `./${appName}/assets/js/index.js`,
      login_css: `./${appName}/assets/css/login.scss`,
    },
    output: {
      path: path.resolve(__dirname, `${appName}/static/${appName}`), // Should be in STATICFILES_DIRS.
      filename: './plugins/cannlytics/[name]-[fullhash].js', // FIXME: contenthash, 
      libraryTarget: 'var',
      library: 'cannlytics', // Turns JavaScript into a module.
      // publicPath: "/static/", // Should match Django STATIC_URL.
    },
    resolve: {
      extensions: ['.js'],
    },
    target: 'node', // Ignore built-in modules like path, fs, etc.
    module: {
      rules: [
        {
          test: /\.s?css$/,
          use: [
            // Optional fix: https://webpack.js.org/guides/asset-modules/
            {
              loader: 'file-loader', // Output CSS.
              options: {
                name: './plugins/cannlytics/[name]-[fullhash].css', // contenthash
                // sourceMap: env.production,
              },
            },
            {
              loader: 'sass-loader', // Compiles Sass to CSS.
              options: {
                // sourceMap: env.production,
                implementation: require('sass'),
                webpackImporter: false,
                sassOptions: {
                  includePaths: ['./node_modules'],
                },
              },
            },
          ],
        },
        {
          test: /\.js$/,
          loader: 'babel-loader', // Convert ES2015 to JavaScript.
          options: {
            "presets": [
              ["@babel/preset-env", {
                "targets": { "esmodules": true }
              }]
            ]
          },
        },
      ],
    },
    optimization: {
      //   runtimeChunk: 'single', // What does this do?
      minimize: true,
      minimizer: [
        new TerserPlugin(),
        new CssMinimizerPlugin({}),
      ],
    },
    plugins: [

      // Make .env variables available in entry file.
      new Dotenv(),

      // Create bundle with hashes.
      new BundleTracker({filename: './webpack-stats.json'}),

      // Use Python to get hashes after the build and insert them into templates
      // using templates and entries specified in build.py.
      {
        apply: (compiler) => {
          compiler.hooks.afterEmit.tap('AfterEmitPlugin', (data) => {
            exec('python build.py', (err, stdout, stderr) => {
              if (stdout) process.stdout.write(stdout);
              if (stderr) process.stderr.write(stderr);
            });
          });
        }
      },
    ],
  }
}
