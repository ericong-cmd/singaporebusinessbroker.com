module.exports = {
  content: ['./src.html'],
  darkMode: 'media',
  theme: { extend: {
    fontFamily: { sans: ['Geist','ui-sans-serif','system-ui','sans-serif'], mono: ['"Geist Mono"','ui-monospace','monospace'] },
    colors: { ink: { DEFAULT:'#0e1a2b', 2:'#2b3a4f', 3:'#5b687a' }, paper: { DEFAULT:'#f6f7f4', 2:'#eef0ec' }, line:'#dfe3dc', accent: { DEFAULT:'#0f6b4f', 2:'#0c5740', soft:'#e3f1ea' } },
    maxWidth: { wrap:'1280px' }, boxShadow: { soft:'0 24px 60px -30px rgba(14,26,43,0.25)' }
  } }
}
