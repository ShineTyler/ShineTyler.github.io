<!--1.前端工程文件夹结构（Tailwind + BEM） -->
project-root/
│
├── public/                     # 静态资源（最终部署）
│   ├── images/
│   ├── icons/
│   └── favicon.ico
│
├── src/
│   ├── assets/
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   │
│   ├── styles/
│   │   ├── base/               # 全局基础样式
│   │   │   ├── reset.css
│   │   │   ├── typography.css
│   │   │   └── variables.css   # 若你需要额外 CSS 变量
│   │   │
│   │   ├── components/         # BEM 组件样式
│   │   │   ├── header.css
│   │   │   ├── hero.css
│   │   │   ├── section.css
│   │   │   ├── post-card.css
│   │   │   ├── project-card.css
│   │   │   └── footer.css
│   │   │
│   │   ├── layouts/            # 页面布局
│   │   │   ├── grid.css
│   │   │   └── container.css
│   │   │
│   │   └── tailwind.css        # Tailwind 入口文件
│   │
│   ├── scripts/
│   │   ├── main.js
│   │   └── lang-switch.js
│   │
│   ├── pages/
│   │   ├── index.html
│   │   ├── about.html
│   │   ├── blog.html
│   │   └── post/
│   │       └── *.html
│   │
│   └── data/
│       ├── posts.json          # 博客文章数据
│       ├── projects.json       # 项目数据
│       └── site.json           # 站点配置（标题、语言等）
│
├── tailwind.config.js
├── package.json
└── README.md


<!--2.设计系统文件夹结构（Design System + Tokens + Figma） -->

design-system/
│
├── tokens/                     # 设计 Token（颜色、字体、间距…）
│   ├── colors.json
│   ├── typography.json
│   ├── spacing.json
│   ├── radius.json
│   └── shadows.json
│
├── components/                 # 设计层面的组件（非代码）
│   ├── atoms/
│   │   ├── button.json
│   │   ├── tag.json
│   │   └── divider.json
│   │
│   ├── molecules/
│   │   ├── post-card.json
│   │   ├── project-card.json
│   │   ├── navbar.json
│   │   └── footer.json
│   │
│   └── layouts/
│       ├── section.json
│       ├── grid.json
│       └── container.json
│
├── figma/                      # Figma 组件库文件（结构说明）
│   ├── component-tree.md
│   ├── naming-rules.md
│   └── export-guidelines.md
│
└── docs/
    ├── design-principles.md
    ├── accessibility.md
    └── usage-guidelines.md

<!-- 3.内容与数据结构（博客 / 项目） -->
content/
│
├── posts/
│   ├── 2026-why-personal-site.md
│   ├── 2026-learning-log.md
│   └── ...
│
├── projects/
│   ├── portfolio-site.md
│   ├── learning-log-system.md
│   └── ...
│
└── meta/
    ├── categories.json
    ├── tags.json
    └── authors.json
