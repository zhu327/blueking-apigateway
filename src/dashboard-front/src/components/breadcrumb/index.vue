<template>
  <div class="bk-breadcrumb" aria-label="Breadcrumb" role="navigation">
    <slot></slot>
  </div>
</template>
<script>
  export default {
    name: 'bk-breadcrumb',
    props: {
      separator: {
        type: String,
        default: '/'
      },
      separatorClass: {
        type: String,
        default: ''
      }
    },
    provide () {
      return {
        bkBreadcrumb: this
      }
    },
    mounted () {
      const items = this.$el.querySelectorAll('.bk-breadcrumb__item')
      if (items.length) {
        items[items.length - 1].setAttribute('aria-current', 'page')
      }
    }
  }
</script>
<style>
    @import "../../ui/breadcrumb.css";
</style>
