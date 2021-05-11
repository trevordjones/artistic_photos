var main = new Vue({
  el: '#home',
  delimiters: ['[[', ']]'],
  data: {
    showArtisticImage: false,
    showStartingImage: true,
    showStyleImage: false,
    showPalette: false,
    showEdit: false,
    image: {},
    styleImage: {},
    artisticImage: {},
    images: [],
    styleImages: [],
    artisticImages: [],
    selected_id: null,
    width: null,
    height: null,
    styleWidth: null,
    styleHeight: null,
    artisticWidth: null,
    artisticHeight: null,
    canvas: {},
    canvasCtx: {},
    rect: {},
    prevX: null,
    prevY: null,
    drag: false,
    canvasImage: null,
    palette: {},
    palettes: [],
    selected_plt_id: null,
  },
  mounted() {
    this.canvas = this.$refs.startingImageCanvas;
    this.canvasCtx = this.canvas.getContext('2d');

    this.$http
      .get('/api/v1/images')
      .then((response) => {
        this.images = response.body.images
        this.filterImages();
      })
    let id = new URL(location.href).searchParams.get('starting');
    if (id != null) {
      this.$http
        .get(`/api/v1/images/${id}`)
        .then((response) => {
          this.image = response.body.image;
          this.setDimensions();
          this.setImageOnCanvas();
        })
    }

    this.$http
      .get('/api/v1/palettes')
      .then(response => this.palettes = response.body.palettes)
  },
  methods: {
    setTab: function(tabName) {
      this.showArtisticImage = tabName == 'artisticImage';
      this.showStartingImage = tabName == 'startingImage';
      this.showStyleImage = tabName == 'styleImage';
      this.showPalette = tabName == 'palette';
      this.showEdit = tabName == 'edit';
    },
    setImageOnCanvas: function(imageUrl) {
      if (imageUrl) {
        this.canvas.toDataURL(imageUrl);
      } else {
        this.canvas.toDataURL(this.image.url);
      }
      this.rect = this.canvas.getBoundingClientRect();
      let img = new Image();
      const vm = this;
      img.onload = function() {
        vm.canvasCtx.drawImage(img, 0, 0, vm.width, vm.height);
        vm.canvasCtx.strokeStyle = 'red';
        vm.canvasCtx.lineWidth = 5;
        vm.canvasCtx.lineCap = 'round';
      }
      if (imageUrl) {
        img.src = imageUrl;
      } else {
        img.src = this.image.url;
      }
    },
    cardHeight: function() {
      if (this.images.length > 8) {
        return 18;
      }

      return this.images.length * 3;
    },
    selectStartingPhoto: function(img) {
      this.$http
        .get(`/api/v1/images/download/${img.id}`)
        .then((response) => {
          this.image = img;
          this.setDimensions();
          this.setImageOnCanvas();
        })
    },
    selectStylePhoto: function(img) {
      this.$http
        .get(`/api/v1/images/download/${img.id}`)
        .then((response) => {
          this.styleImage = img;
          this.setStyleDimensions();
        })
    },
    selectArtisticPhoto: function(img) {
      this.$http
        .get(`/api/v1/images/download/${img.id}`)
        .then((response) => {
          this.artisticImage = img;
          this.setArtisticDimensions();
        })
    },
    selectPalette: function(plt) {
      this.selected_plt_id = plt.id;
      this.palette = plt;
    },
    setDimensions: function() {
      const maxWidth = 600;
      const maxHeight = 600;
      let ratio = Math.min(maxWidth / this.image.width, maxHeight / this.image.height);
      this.width = this.image.width * ratio;
      this.height = this.image.height * ratio;
    },
    setStyleDimensions: function() {
      const maxWidth = 600;
      const maxHeight = 600;
      let ratio = Math.min(maxWidth / this.styleImage.width, maxHeight / this.styleImage.height);
      this.styleWidth = this.styleImage.width * ratio;
      this.styleHeight = this.styleImage.height * ratio;
    },
    setArtisticDimensions: function() {
      const maxWidth = 600;
      const maxHeight = 600;
      let ratio = Math.min(maxWidth / this.artisticImage.width, maxHeight / this.artisticImage.height);
      // this.artisticWidth = this.artisticImage.width * ratio;
      // this.artisticHeight = this.artisticImage.height * ratio;
      this.artisticWidth = this.artisticImage.width;
      this.artisticHeight = this.artisticImage.height;
    },
    setDrag: function() {
      this.drag = true;
    },
    dragLine: function(event) {
      if (this.drag) {
        this.canvasCtx.beginPath();
        const x = event.clientX - this.rect.left;
        const y = event.clientY - this.rect.top;
        if (x != this.prevX || y != this.prevY) {
          if (this.prevX != null) {
            this.canvasCtx.moveTo(this.prevX, this.prevY);
            this.canvasCtx.lineTo(x, y);
            this.canvasCtx.stroke();
          }
        }
        this.prevX = x;
        this.prevY = y;
      }
    },
    unsetDrag: function(event) {
      this.drag = false;
      this.prevX = null;
      this.prevY = null;
      this.canvasImage = this.canvas.toDataURL();
      this.setImageOnCanvas(this.canvas.toDataURL());
    },
    filterImages: function() {
      this.styleImages = this.images.filter(img => img.subdirectory == 'style');
      this.artisticImages = this.images.filter(img => img.subdirectory == 'artistic');
    },
    paletteWidth: function() {
      const maxWidth = 600;
      return maxWidth / this.palette.hex_values.length;
    }
  }
})
