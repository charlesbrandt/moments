;;;; THINGS THAT ONLY NEED TO BE RUN ONCE (AT STARTUP) GO HERE

;; Notes about ';' and comments:
;; https://www.gnu.org/software/emacs/manual/html_node/elisp/Comment-Tips.html
;; (single ';' are meant to be to the right)

;; set load-path .emacs.d/ first
(setq load-path (cons "~/.emacs.d/" load-path))


;; customizations [custom lisp code snippets to modify editor behavior]
;; that are updated as various processes are refined
;; should go in ~/.emacs.d/context.el

;; these can then be easily reloaded in the editor without restarting the editor
;; there is a "M-x reload" function for that.
;; reloading can also be accomplished by selecting the region below,
;; then executing it using the "Emacs-Lisp->Evaluate Region" option/command

(setq web-mode-markup-indent-offset 2)
(setq web-mode-css-indent-offset 2)
(setq web-mode-code-indent-offset 2)

;JAVASCRIPT
;http://stackoverflow.com/questions/4177929/how-to-change-the-indentation-width-in-emacs-javascript-mode
(setq js-indent-level 2)


;; Emacs Lisp Package Archive

;; https://www.emacswiki.org/emacs/ELPA
;; https://melpa.org/#/getting-started
(require 'package) 
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))
(package-initialize)

;; via: http://wikemacs.org/wiki/Package.el

;; may be able to accomplish the following with:
;; https://github.com/jwiegley/use-package

(require 'cl-lib)

(defvar my-packages
  ;; todo: consider these packages
  ;; '(ack-and-a-half auctex clojure-mode coffee-mode deft expand-region
  ;;                  gist groovy-mode haml-mode haskell-mode inf-ruby
  ;;                  magit magithub markdown-mode paredit projectile python
  ;;                  sass-mode rainbow-mode scss-mode solarized-theme
  ;;                  volatile-highlights yaml-mode yari zenburn-theme)
  '(python markdown-mode sass-mode scss-mode yaml-mode web-mode vue-mode)
  "A list of packages to ensure are installed at launch.")
  ;; https://github.com/AdamNiederer/vue-mode

(defun my-packages-installed-p ()
  (cl-loop for p in my-packages
           when (not (package-installed-p p)) do (cl-return nil)
           finally (cl-return t)))

(unless (my-packages-installed-p)
  ;; check for new packages (package versions)
  (package-refresh-contents)
  ;; install the missing packages
  (dolist (p my-packages)
    (when (not (package-installed-p p))
      (package-install p))))


;(autoload 'context)
(load-file "~/.emacs.d/context.el")


(tool-bar-mode -1) 
(put 'upcase-region 'disabled nil)
(put 'downcase-region 'disabled nil)

(setq mac-option-key-is-meta nil) 
(setq mac-command-key-is-meta t) 
(setq mac-command-modifier 'meta) 
(setq mac-option-modifier nil) 

;; newer versions of emacs are opening new frames for multiple files
;; this suppresses that behavior
(setq ns-pop-up-frames nil)

;; Prevent accidentally killing emacs.
(global-set-key [(control x) (control c)]
                '(lambda ()
                   (interactive)
                   (if (y-or-n-p-with-timeout "Do you really want to exit Emacs ? " 4 nil)
                   
    (save-buffers-kill-emacs))))

(add-hook 'text-mode-hook 'flyspell-mode) 

;http://www.emacswiki.org/cgi-bin/wiki/RecentFiles
(require 'recentf)
(recentf-mode 1)

; Tab completion:
; http://www.emacswiki.org/cgi-bin/wiki/Icicles
; consider investigating icicles


;*2012.02.05 14:25:26 
; switch to only one window (in the emacs sense) open (one editing panel)
; (delete-other-windows) is what ctl-x 1 does
; but it must happen too early in the sequence (before other files are loaded)
; 
; this works:
(add-hook 'window-setup-hook 'delete-other-windows)
; via: 
; http://stackoverflow.com/questions/1144729/how-do-i-prevent-emacs-from-horizontally-splitting-the-screen-when-opening-multi


;;;; Themes

;; (load-file "~/.emacs.d/theme.el")

;; ;keeping this around to undo the bad settings done elsewhere
;; (my-color-theme-light)

;https://github.com/whitlockjc/atom-dark-theme-emacs
(load-file "~/.emacs.d/atom-dark-theme.el")

;(color-theme-calm-forest)
;;set default color theme
;
;(color-theme-gray30)
;(color-theme-calm-forest)
;(color-theme-euphoria)

;;black bagkgrounds:netbook
;(color-theme-oswald)
;(color-theme-lawrence)
;(color-theme-hober)
;(color-theme-charcoal-black)
;(color-theme-black)
;(color-theme-billw)
;(color-theme-midnight)
;(color-theme-late-night)



;;; Frame size:

;; this works, but will probably be global for all instances
;; unless frame-setup overrides
;(set-frame-height (selected-frame) 43)
;(set-frame-width (selected-frame) 80)

(message "SYSTEM NAME:")
(setq hostname (car (split-string (system-name) "\\.")))
(message hostname)

;; frame setup for different computers
;(defun setup-frame-for (name h w font)
(defun setup-frame-for (name h w)
  (if (equal hostname name)
      (progn
        (set-frame-height (selected-frame) h)
        (set-frame-width (selected-frame) w)
	;; this applies the height to new frames too 
	(add-to-list 'default-frame-alist (cons 'height h))
	(add-to-list 'default-frame-alist (cons 'width w))
	;(custom-set-faces font)
	)
    )
  )

(defun frame-setup (list)
  (when window-system
    (dolist (conf list)
      ;(setup-frame-for (car conf) (cadr conf) (caddr conf)))))
      ;(setup-frame-for (car conf) (cadr conf) (caddr conf) (cadddr conf) ))))

      ;(setup-frame-for (car conf) (cadr conf) (cadr (cdr conf)) (cadr (cdr (cdr conf))) ))))
      (setup-frame-for (car conf) (cadr conf) (cadr (cdr conf)) ))))


;(name height width font)
;where height and width are for the frame
(frame-setup
 '(("blank" 29 98 '() ) ;; example
   ("drishti" 34 125 ) ;; netbook
   ("context" 32 80  ) ;; laptop
   ("breathe" 43 80  )
   )
)

;:height 97 :width normal :foundry "unknown" 




;; Customize Indentation levels via Emacs:
;; M-x customize
;; Then, choose "Programming," and then "Languages," and then select a language/mode to customize. Edit the options as you see fit. When done, choose either "Save for current session" or "Save for future sessions."
;; via: http://stackoverflow.com/questions/4177929/how-to-change-the-indentation-width-in-emacs-javascript-mode

;; https://emacs.stackexchange.com/questions/21095/how-do-i-make-javascript-mode-not-turn-all-8-spaces-into-tabs
;; This didn't seem to have the desired effect. Next section sets it globally
(defun my-js-mode-hook ()
  "Custom `js-mode' behaviours."
  (setq indent-tabs-mode nil))
(add-hook 'js-mode-hook 'my-js-mode-hook)

;; previously set in programming.el
;; need it either way!
(setq-default indent-tabs-mode nil)

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(ansi-color-names-vector
   ["#242424" "#E5786D" "#95E454" "#CAE682" "#8AC6F2" "#333366" "#CCAA8F" "#F6F3E8"])
 '(custom-enabled-themes nil)
 '(global-font-lock-mode t)
 '(inhibit-startup-screen t)
 '(js-indent-level 2)
 '(tool-bar-mode nil))

;; (custom-set-faces
;;  ;; custom-set-faces was added by Custom.
;;  ;; If you edit it by hand, you could mess it up, so be careful.
;;  ;; Your init file should contain only one such instance.
;;  ;; If there is more than one, they won't work right.
;;  '(default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :family "Monaco")))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
