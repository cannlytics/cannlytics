# Style

Style distinguishes one site from another. You are free and encouraged to modify the style to create a site that is uniquely yours.


## Themes

[Bootswatch](https://bootswatch.com/help/) provides many great themes. The [pulse theme](https://bootswatch.com/pulse/) is the default theme of the personal website.


## Design Patterns

- Cut-out illustrations
  * Humanize technology

- Waves between sections
  * [Waves with CSS](https://stackoverflow.com/questions/17202548/wavy-shape-with-css)
  * [Wave Generator](https://smooth.ie/blogs/news/svg-wavey-transitions-between-sections)


## Colors

* Orange: #ff5733
* Light Orange: #ffa600
* Dark Orange: #e53a23
* Green: #45B649
* Light Green: #96e6a1
* Dark Green: #3f7f34
* Darkest Green: #104607

Color resources:

* [Gradients (UI)](https://uigradients.com/#KyooTah)
* [Gradients (Web)](https://webgradients.com/)
* [CSS Transparency](https://stackoverflow.com/questions/23201134/transparent-argb-hex-value)
* [Encycolorpedia](https://encycolorpedia.com/)
* [Paletton](https://paletton.com/)
* [HTML Color Codes](https://htmlcolorcodes.com/)


## Fonts

Serif fonts:

* [Cinzel Decorative (Brand Title)](https://fonts.google.com/specimen/Cinzel+Decorative)
* [Cinzel (Special Titles)](https://fonts.google.com/specimen/Cinzel)
* [Libre Baskerville (Body)](https://fonts.google.com/specimen/Libre+Baskerville)

Sans-serif fonts:

* [Libre Franklin (Headlines)](https://fonts.google.com/specimen/Libre+Franklin)
* [Montserrat](https://fonts.google.com/specimen/Montserrat?query=Montserrat)

Resources:

* [Typewolf](https://www.typewolf.com/)


## CSS

[Bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/) is used for styling templates. You can install Bootstrap with:

```shell

npm install bootstrap
npm install style-loader --save

```

[Material Components](https://github.com/material-components/material-components-web) are used for certain widgets. Material components provide beautiful animations and useful Google-style widgets.

You can install material components with:

```shell

npm i material-components-web

```

You can install material components dependencies with:

```shell

npm install --save-dev webpack webpack-cli webpack-dev-server css-loader sass-loader sass extract-loader file-loader autoprefixer postcss-loader @babel/core babel-loader @babel/preset-env

```


## Icons

SVG formats are preferred. This imposes a IE 9+ / Android 3+ restriction. If you want to ensure browser support for older browsers, then icon fonts may be preferrable.

<!-- "IcoMoon, which is known for producing icon fonts, actually does a fantastic job of producing SVG sprites as well. After selecting all the fonts you want, click the SVG button on the bottom and you’ll get that output, including a demo page with the inline SVG method." -->

A build method that is simple and effective is to keep a repository of SVG icons and inline an SVG when it is needed.

Useful icon packages:

* [Feather Icons](https://feathericons.com/)
* [Hawcons](http://hawcons.com/preview/)
* [IcoMoon](https://icomoon.io/#docs)
* [Octicons](https://primer.style/octicons/)
* [Zondicons](http://www.zondicons.com/)

Resources:

* [SVG Images in Django](https://stackoverflow.com/questions/25954797/svg-img-src-with-django)
* [SVG Sprites](https://css-tricks.com/svg-sprites-use-better-icon-fonts/)
* [Icon Fonts vs. SVGs](https://css-tricks.com/icon-fonts-vs-svg/)


## Python Code Style

[The *Black* Code Style](https://black.readthedocs.io/en/stable/installation_and_usage.html) is used for Python code.
