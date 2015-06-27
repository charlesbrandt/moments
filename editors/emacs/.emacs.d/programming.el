;============================
; Programming MODES
;============================

;use spaces instead of tabs:
;http://stackoverflow.com/questions/45861/how-do-i-get-js2-mode-to-use-spaces-instead-of-tabs-in-emacs
(setq-default indent-tabs-mode nil)

;PYTHON
(setq auto-mode-alist (cons '("\\.py$" . python-mode) auto-mode-alist))
(setq interpreter-mode-alist (cons '("python" . python-mode) interpreter-mode-alist))
(autoload 'python-mode "python-mode" "Python editing mode." t)

;(add-to-list 'auto-mode-alist '("\\.zpt$" . html-mode))
;(add-to-list 'auto-mode-alist '("\\.pt$" . html-mode))
;(add-to-list 'auto-mode-alist '("\\.dtml$" . html-mode))
;(add-to-list 'auto-mode-alist '("\\.mako$" . html-mode))
;(add-to-list 'auto-mode-alist '("\\.tpl$" . html-mode))

;(add-to-list 'auto-mode-alist '("\\.less$" . css-mode))

;http://web-mode.org/
(require 'web-mode)
(add-to-list 'auto-mode-alist '("\\.zpt$" . web-mode))
(add-to-list 'auto-mode-alist '("\\.pt$" . web-mode))
(add-to-list 'auto-mode-alist '("\\.dtml$" . web-mode))
(add-to-list 'auto-mode-alist '("\\.mako$" . web-mode))
(add-to-list 'auto-mode-alist '("\\.tpl$" . web-mode))
(add-to-list 'auto-mode-alist '("\\.tag$" . web-mode))

(add-to-list 'auto-mode-alist '("\\.html?\\'" . web-mode))
(add-to-list 'auto-mode-alist '("\\.jsx$" . web-mode))
(add-to-list 'auto-mode-alist '("\\.less$" . web-mode))

(setq web-mode-engines-alist
      '(("css" . "\\.less$")
        )
)

(setq web-mode-content-types-alist
  '(("css" . "\\.less$")
    )
)


(setq web-mode-markup-indent-offset 2)
(setq web-mode-css-indent-offset 2)
(setq web-mode-code-indent-offset 2)

;JAVASCRIPT
;http://stackoverflow.com/questions/4177929/how-to-change-the-indentation-width-in-emacs-javascript-mode
(setq js-indent-level 2)

;react based jsx files mode:
;https://github.com/jsx/jsx-mode.el
;(add-to-list 'auto-mode-alist '("\\.jsx\\'" . jsx-mode))
;(autoload 'jsx-mode "jsx-mode" "JSX mode" t)

;https://github.com/mooz/js2-mode
;; (load-file "~/.emacs.d/js2-mode.el")
;; (load-file "~/.emacs.d/js2-imenu-extras.el")
;; (add-to-list 'auto-mode-alist '("\\.js\\'" . js2-mode))

;; ;http://feeding.cloud.geek.nz/posts/proper-indentation-of-javascript-files/
;; (custom-set-variables  
;;  '(js2-basic-offset 2)  
;;  '(js2-bounce-indent-p t)  
;; )

;C/ARDUINO
(add-to-list 'auto-mode-alist '("\\.ino$" . c-mode)) 



;call any other programming modes you need here:

;SASS
;(load-file "~/.emacs.d/scss-mode.el")
;;; scss-mode.el --- Major mode for editing SCSS files
;;
;; Author: Anton Johansson <anton.johansson@gmail.com> - http://antonj.se
;; URL: https://github.com/antonj/scss-mode
;; Created: Sep 1 23:11:26 2010
;; Version: 0.5.0
;; Keywords: scss css mode
;;
;; This program is free software; you can redistribute it and/or
;; modify it under the terms of the GNU General Public License as
;; published by the Free Software Foundation; either version 2 of
;; the License, or (at your option) any later version.
;;
;; This program is distributed in the hope that it will be
;; useful, but WITHOUT ANY WARRANTY; without even the implied
;; warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
;; PURPOSE.  See the GNU General Public License for more details.

;; (defconst scss-font-lock-keywords
;;   ;; Variables
;;   '(("$[a-z_-][a-z-_0-9]*" . font-lock-constant-face)))

;; (define-derived-mode scss-mode css-mode "SCSS"
;;   "Major mode for editing SCSS files, http://sass-lang.com/
;; Special commands:
;; \\{scss-mode-map}"
;;   (font-lock-add-keywords nil scss-font-lock-keywords)
;;   ;; Add the single-line comment syntax ('//', ends with newline)
;;   ;; as comment style 'b' (see "Syntax Flags" in elisp manual)
;;   (modify-syntax-entry ?/ ". 124" css-mode-syntax-table)
;;   (modify-syntax-entry ?* ". 23b" css-mode-syntax-table)
;;   (modify-syntax-entry ?\n ">" css-mode-syntax-table)
;;   ;(add-to-list 'compilation-error-regexp-alist scss-compile-error-regex)
;;   ;(add-hook 'after-save-hook 'scss-compile-maybe nil t)
;;   )

;; (add-to-list 'auto-mode-alist '("\\.scss$" . scss-mode))
;; (add-to-list 'auto-mode-alist '("\\.sass$" . scss-mode))

;MATLAB
;(add-to-list 'load-path "~/.emacs.d/matlab-emacs")
;(require 'matlab-load)

;(autoload 'matlab-mode "matlab" "Enter MATLAB mode." t)
;(setq auto-mode-alist (cons '("\\.m\\'" . matlab-mode) auto-mode-alist))
;(autoload 'matlab-shell "matlab" "Interactive MATLAB mode." t)

;User Level customizations (You need not use them all):
;(setq matlab-indent-function-body t)  ; if you want function bodies indented

;(setq matlab-verify-on-save-flag nil) ; turn off auto-verify on save
;(defun my-matlab-mode-hook ()
;  (setq fill-column 76))              ; where auto-fill should wrap
;(add-hook 'matlab-mode-hook 'my-matlab-mode-hook)
;(defun my-matlab-shell-mode-hook ()
;  '())
;(add-hook 'matlab-shell-mode-hook 'my-matlab-shell-mode-hook)
