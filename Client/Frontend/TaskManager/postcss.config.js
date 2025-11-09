export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    // CSS minification and optimization in production
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {
      preset: ['default', {
        discardComments: {
          removeAll: true,
        },
        normalizeWhitespace: true,
        minifyFontValues: true,
        minifyGradients: true,
      }]
    }} : {})
  },
}
