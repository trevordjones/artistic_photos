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
    canvasImageUrl: null,
    rect: {},
    prevX: null,
    prevY: null,
    drag: false,
    canvasImage: null,
    palette: {},
    palettes: [],
    selected_plt_id: null,
    showPaletteMapping: false,
    fromHtmlHexes: null,
    targetHtmlHexes: null,
    paletteSelections: [],
    hexValues: [],
    nstOption: 1,
    nstOptions: [1, 2, 3, 4, 5],
    showNstOptions: false,
    showNstHelp: false,
    showDeletePaletteModal: false,
    showDeleteImageModal: false,
    searchImages: [],
    searchTerm: ""

  },
  updated() {
    if (this.showStartingImage) {
      this.canvas = this.$refs.startingImageCanvas;
      this.canvasCtx = this.canvas.getContext('2d');
      this.setImageOnCanvas(this.canvasImageUrl);
    }
  },
  mounted() {
    this.canvas = this.$refs.startingImageCanvas;
    this.canvasCtx = this.canvas.getContext('2d');

    this.$http
      .get('/api/v1/images')
      .then((response) => {
        this.images = response.body.images
        this.searchImages = response.body.images
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

    let tab = new URL(location.href).searchParams.get('tab');
    if (tab != null) {
      this.setTab(tab);
    }

    this.$http
      .get('/api/v1/palettes')
      .then(response => this.palettes = response.body.palettes)
  },
  methods: {
    setTab: function(tabName) {
      this.showArtisticImage = tabName == 'artistic';
      this.showStartingImage = tabName == 'starting';
      this.showStyleImage = tabName == 'style';
      this.showPalette = tabName == 'palette';
      this.showEdit = tabName == 'edit';
      window.history.replaceState(null, null, window.location.pathname);
    },
    setImageOnCanvas: function(imageUrl) {
      if (imageUrl) {
        this.canvasImageUrl = imageUrl;
      } else {
        this.canvasImageUrl = this.image.url;
      }

      this.canvas.toDataURL(this.canvasImageUrl);
      this.rect = this.canvas.getBoundingClientRect();
      let img = new Image();
      const vm = this;
      img.onload = function() {
        vm.canvasCtx.drawImage(img, 0, 0, vm.width, vm.height);
        vm.canvasCtx.strokeStyle = 'red';
        vm.canvasCtx.lineWidth = 5;
        vm.canvasCtx.lineCap = 'round';
      }

      img.src = this.canvasImageUrl;
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
      this.artisticWidth = this.artisticImage.width * ratio;
      this.artisticHeight = this.artisticImage.height * ratio;
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
    },
    togglePaletteMapping: function() {
      this.showPaletteMapping = !this.showPaletteMapping;
      this.drawFromPalette();
      if (this.showPaletteMapping) {
        this.$http
          .get(`/api/v1/palettes/${this.image.id}/images`)
          .then((response) => {
            this.targetPalette = response.body.palette;
            this.drawTargetPalette();
          })
          .catch(() => {
            this.targetPalette = {}
            this.targetHtmlHexes = null;
          })
      }
    },
    drawFromPalette: function() {
      if (this.palette.hex_values) {
        const width = 100 - this.palette.hex_values.length
        this.fromHexWidth = width / this.palette.hex_values.length;
        this.fromHtmlHexes = [];
        let html;
        this.palette.hex_values.forEach(hex => {
          html = [`<span></span>`, hex];
          this.fromHtmlHexes.push(html);
        })
      }
    },
    drawTargetPalette: function() {
      const width = 100 - this.targetPalette.hex_values.length
      if (this.targetPalette.hex_values) {
        this.targetHexWidth = width / this.targetPalette.hex_values.length;
        let html;
        this.targetHtmlHexes = [];
        this.targetPalette.hex_values.forEach(hex => {
          html = ['<span></span>', hex];
          this.targetHtmlHexes.push(html);
        })
      }
    },
    selectFrom: function(event, hex) {
      exit = false;
      this.paletteSelections.forEach((selection, idx) => {
        if (event.target == selection.from.element) {
          exit = true;
          this.fromSelect = null;
        }
      })

      if (exit) { return; }

      if (this.fromSelect && this.fromSelect.element == event.target) {
        event.target.style.outline = null;
        this.fromSelect = null;
      } else {
        event.target.style.outline = "4px solid #333";
        if (this.fromSelect) {
          this.fromSelect.element.style.outline = null;
        }
        console.log(hex)
        this.fromSelect = {element: event.target, hex: hex};
      }
    },
    selectTarget: function(event, hex) {
      exit = false;
      this.paletteSelections.forEach((selection, idx) => {
        if (selection.target == event.target) {
          if (this.fromSelect) {
            exit = true;
          } else {
            selection.from.element.style.outline = "thick solid #333";
            selection.target.style.outline = null;
            this.fromSelect = selection.from;
            this.paletteSelections.splice(idx, 1);
            this.hexValues.splice(idx, 1);
            exit = true;
          }
        }
      });

      if (exit || !(this.fromSelect)) { return; }

      if (this.targetSelect == event.target) {
        event.target.style.outline = null;
        this.targetSelect = null;
        this.fromSelect.element.style.outline = "thick solid #333";
      } else {
        event.target.style.outline = `thick solid ${this.fromSelect.hex}`;
        this.fromSelect.element.style.outline = `thick solid ${hex}`;
        this.paletteSelections.push(
          {
            from: this.fromSelect,
            target: event.target,
          },
        )
        this.hexValues.push(`${this.fromSelect.hex}-${hex}`)

        this.fromSelect = null;
      }
    },
    verifyDeletePalette: function(palette) {
      this.showDeletePaletteModal = true;
      this.deletedPalette = palette;
    },
    deletePalette: function() {
      let index = this.palettes.indexOf(this.deletedPalette);
      vm = this;
      this.$http
        .delete(`/api/v1/palettes/${vm.deletedPalette.id}`)
        .then(() => {
          vm.palettes.splice(index, 1);
          vm.palette = {};
          vm.showDeletePaletteModal = false;
          vm.deletedPalette = null;
        })
    },
    closeDeletePaletteModal: function() {
      this.showDeletePaletteModal = false;
      this.deletedPalette = null;
    },
    verifyDeleteImage: function(img){
      this.showDeleteImageModal = true;
      this.deletedImage = img;
    },
    deleteImage: function(){
      let index = this.images.indexOf(this.deletedImage);
      let artistic_index = this.artisticImages.indexOf(this.deletedImage);
      vm = this;
      this.$http
        .delete(`/api/v1/images/${vm.deletedImage.id}`)
        .then(() => {
          vm.images.splice(index, 1);
          vm.image = {};
          vm.showDeleteImageModal = false;
          vm.deletedImage = null;
          vm.artisticImages.splice(artistic_index, 1);
          vm.artisticImage = {};
          location.reload();
        })
    },
    closeDeleteImageModal: function() {
      this.showDeleteImageModal = false;
      this.deletedImage = null;
    },
    searchImage: function(input) {
      this.searchImages = [];
      this.searchTerm = input.toLowerCase();
      if(!this.searchTerm.length){
        this.searchImages = this.images;
      } else{
          for(i=0; i<this.images.length; i++){
            if(this.images[i].name.toLowerCase().startsWith(this.searchTerm)){
              this.searchImages.push(this.images[i])
          }
        }
      }
    },
  }
})
