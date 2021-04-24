var main = new Vue({
  el: '#home',
  delimiters: ['[[', ']]'],
  data: {
    message: 'hello vue',
    image: {},
    images: [],
    selected_id: null,
  },
  mounted() {
    this.$http
      .get('/api/v1/images')
      .then(response => this.images = response.body.images)
    let id = new URL(location.href).searchParams.get('starting');
    if (id != null) {
      this.$http
        .get(`/api/v1/images/${id}`)
        .then((response) => {
          this.image = response.body.image;
          this.selected_id = id;
        })
    }
  },
  methods: {
    cardHeight: function() {
      if (this.images.length > 8) {
        return 18;
      }

      return this.images.length * 3;
    },
    selectPhoto: function(img) {
      this.selected_id = img.id;
      this.image = img;
    }
  }
})
