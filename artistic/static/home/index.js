var main = new Vue({
  el: '#home',
  delimiters: ['[[', ']]'],
  data: {
    message: 'hello vue',
    image: {},
    images: [],
  },
  mounted() {
    this.$http
      .get('/api/v1/images')
      .then(response => this.images = response.body.images)
    let id = new URL(location.href).searchParams.get('name');
    if (id != null) {
      this.$http
        .get(`/api/v1/images/${id}`)
        .then(response => this.image = response.body.image)
    }
  }
})
