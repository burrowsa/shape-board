<template>
  <div id="app">
    <b-navbar toggleable="md" type="dark" variant="info">
      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

      <b-navbar-brand href="#">Shape Board</b-navbar-brand>

      <b-collapse is-nav id="nav_collapse">
        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">
          <b-nav-item-dropdown :text="shape" right v-for="shape in ['circle', 'triangle', 'square', 'rectangle']" :key="shape" class="caps">
            <b-dropdown-item v-on:click="addRandomShape(shape, color)" v-for="color in ['red', 'yellow', 'green', 'blue', 'black']" :key="color" :class="`caps ${color}`">{{color}}</b-dropdown-item>
          </b-nav-item-dropdown>

          <b-nav-item v-on:click="clear" right>Clear</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>

    <div id="board">
      <svg :width="width" :height="height">
        <template v-for="shape in shapes">
          <circle :cx="shape.x" :cy="shape.y" :r="shape.r" :fill="shape.color" :stroke="shape.outline" stroke-width="1" v-if="shape.type=='circle'" v-bind:key="shape"/>
          <rect :x="shape.x - shape.side/2" :y="shape.y - shape.side/2"
                :width="shape.side" :height="shape.side" :fill="shape.color" :stroke="shape.outline" stroke-width="1" v-if="shape.type=='square'" v-bind:key="shape"/>
          <rect :x="shape.x - shape.width/2" :y="shape.y - shape.height/2"
                :width="shape.width" :height="shape.height" :fill="shape.color" :stroke="shape.outline" stroke-width="1" v-if="shape.type=='rectangle'" v-bind:key="shape"/>
          <polygon :points="`${shape.x - shape.side/2}, ${shape.y + shape.side/2 * Math.sin(Math.PI/6)}
                              ${shape.x + shape.side/2}, ${shape.y + shape.side/2 * Math.sin(Math.PI/6)}
                              ${shape.x}, ${shape.y - shape.side/2 * Math.sin(Math.PI/6)}`"
                              :fill="shape.color" :stroke="shape.outline" stroke-width="1" v-if="shape.type=='triangle'" v-bind:key="shape"/>
        </template>
        Sorry, your browser does not support inline SVG. 
      </svg>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import { Navbar } from 'bootstrap-vue/es/components'
import axios from 'axios'
import io from 'socket.io-client'

Vue.use(Navbar)

const shapes = []

const socket = io(location.protocol + '//' + document.domain + ':' + location.port + '/v1')

socket.on('update', function (data) {
  while (shapes.length) {
    shapes.pop()
  }

  data.forEach(function (element) {
    shapes.push(element)
  })
})

socket.on('error', function (msg) {
  Vue.toast(msg, {
    className: 'et-alert',
    horizontalPosition: 'center'
  })
})

function errorToast (promise) {
  promise.catch(e => {
    Vue.toast(e, {
      className: 'et-alert',
      horizontalPosition: 'center'
    })
  })
}

function randInRange (min, max) {
  return Math.random() * (max - min) + min
}

export default {
  name: 'shapeBoard',
  data () {
    return {
      shapes,
      width: 600,
      height: 400,
      minDimension: 10
    }
  },
  methods: {
    addRandomShape (type, color) {
      const shape = {
        type,
        color,
        x: randInRange(0, this.width),
        y: randInRange(0, this.height)
      }

      if (color === 'black') {
        shape.outline = 'white'
      } else {
        shape.outline = 'black'
      }

      if (type === 'circle') {
        shape.r = randInRange(this.minDimension, Math.min(this.width, this.height) / 4)
      } else if (type === 'rectangle') {
        shape.width = randInRange(this.minDimension, this.width)
        shape.height = randInRange(this.minDimension, this.height)
      } else {
        shape.side = randInRange(this.minDimension, Math.min(this.width, this.height) / 2)
      }

      errorToast(axios.post('/api/add_shape', shape))
    },
    clear () {
      errorToast(axios.get('/api/clear_shapes'))
    }
  }
}
</script>

<style>
.red {
  color: red !important;
}

.green {
  color: green !important;
}

.blue {
  color: blue !important;
}

.black {
  color: black !important;
}

.yellow {
  color: yellow !important;
}

.caps {
  text-transform: capitalize;
}

body, html, #board, #app {
  height: 100%;
}

#board {
  position: relative;
}

svg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  border-width: 1px;
  border-style: solid;
}

</style>
