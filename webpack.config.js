const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  entry: {
    index: "./src/index.tsx",
    admin: "./src/admin.tsx",
  },
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].js", // => index.js и admin.js
    clean: true,
  },
  mode: "development",
  devServer: {
    historyApiFallback: {
      rewrites: [
        { from: /^\/admin.*$/, to: '/admin.html' }
      ],
    },
    static: path.resolve(__dirname, "dist"),
    port: 3000,
    hot: true,
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(png|jpg|gif|svg|webp)$/,
        type: "asset/resource",
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./public/index.html",
      filename: "index.html",
      chunks: ["index"], // подключаем только index.js
    }),
    new HtmlWebpackPlugin({
      template: "./public/admin.html",
      filename: "admin.html",
      chunks: ["admin"], // подключаем только admin.js
    }),
  ],
};
