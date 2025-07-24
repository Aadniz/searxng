#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later

themes.help(){
    cat <<EOF
themes.:
  all       : test & build all themes
  simple    : test & build simple theme
  red-floof : test & build red-floof theme
  lint      : lint JS & CSS (LESS) files
  fix       : fix JS & CSS (LESS) files
  test      : test all themes
EOF
}

themes.all() {
    (   set -e
        vite.simple.build
        vite.red-floof.build
    )
    dump_return $?
}

themes.simple() {
    (   set -e
        build_msg SIMPLE "theme: run build (simple)"
        vite.simple.build
    )
    dump_return $?
}

themes.red-floof() {
    (   set -e
        build_msg RED_FLOOF "theme: run build (simple)"
        vite.red-floof.build
    )
    dump_return $?
}

themes.fix() {
    (   set -e
        build_msg SIMPLE "theme: fix (all themes)"
        vite.simple.fix
        build_msg RED_FLOOF "theme: fix (all themes)"
        vite.red-floof.fix
    )
    dump_return $?
}

themes.lint() {
    (   set -e
        build_msg SIMPLE "theme: lint (all themes)"
        vite.simple.lint
        build_msg RED_FLOOF "theme: lint (all themes)"
        vite.red-floof.lint
    )
    dump_return $?
}

themes.test() {
    (   set -e
        # we run a build to test (in CI)
        build_msg SIMPLE "theme: run build (to test)"
        vite.simple.build
        build_msg RED_FLOOF "theme: run build (to test)"
        vite.red-floof.build
    )
    dump_return $?
}
