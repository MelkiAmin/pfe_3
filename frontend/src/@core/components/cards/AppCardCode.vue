<script lang="ts" setup>
import { getSingletonHighlighter } from 'shiki'
import { PerfectScrollbar } from 'vue3-perfect-scrollbar'

type CodeLanguages = 'ts' | 'js'

interface Props {
  title: string
  code: CodeProp
  codeLanguage?: string
  noPadding?: boolean
}

type CodeProp = Record<CodeLanguages, string>

const props = withDefaults(defineProps<Props>(), {
  codeLanguage: 'markup',
  noPadding: false,
})

const preferredCodeLanguage = useCookie<CodeLanguages>('preferredCodeLanguage', {
  default: () => 'ts',
  maxAge: COOKIE_MAX_AGE_1_YEAR,
})

const isCodeShown = ref(false)

const { copy, copied } = useClipboard({ source: computed(() => props.code[preferredCodeLanguage.value]) })

const highlighter = await getSingletonHighlighter({
  themes: ['dracula', 'dracula-soft'],
  langs: ['vue'],
})

const codeSnippet = computed(() =>
  highlighter.codeToHtml(props.code[preferredCodeLanguage.value], {
    lang: 'vue',
    theme: 'dracula',
  }),
)
</script>

<template>

