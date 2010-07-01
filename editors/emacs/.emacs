;THINGS THAT ONLY NEED TO BE RUN ONCE (AT STARTUP) GO HERE

; customizations [custom lisp code snippets to modify editor behavior]
; that are updated as various processes are refined
; should go in ~/.emacs.d/context.el
;
; these can then be easily reloaded in the editor without restarting the editor
; there is a "M-x reload" function for that.
; reloading can also be accomplished by selecting the region below,
; then executing it using the "Emacs-Lisp->Evaluate Region" option/command
(setq load-path (cons "~/.emacs.d/" load-path))

(tool-bar-mode)

;; Prevent accidentally killing emacs.
(global-set-key [(control x) (control c)]
                '(lambda ()
                   (interactive)
                   (if (y-or-n-p-with-timeout "Do you really want to exit Emacs ? " 4 nil)
                       (save-buffers-kill-emacs))))

;;(autoload 'context)
(load-file "~/.emacs.d/context.el")

(add-hook 'text-mode-hook 'flyspell-mode) 

;http://www.emacswiki.org/cgi-bin/wiki/RecentFiles
(require 'recentf)
(recentf-mode 1)
;http://www.emacswiki.org/cgi-bin/wiki/Icicles
;need to investigate icicles

(custom-set-variables
  ;; custom-set-variables was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(global-font-lock-mode t)
 '(inhibit-startup-screen t))

(load-file "~/.emacs.d/theme.el")

;keeping this around to undo the bad settings done elsewhere
(my-color-theme-light)

(frame-setup
 '(("drishti"  29 98) ;; my netbook
   ))

;(color-theme-calm-forest)
;;set default color theme
;
;(color-theme-gray30)
;(color-theme-calm-forest)
;(color-theme-euphoria)

;;black bagkgrounds:
;(color-theme-oswald)
;(color-theme-lawrence)
;(color-theme-hober)
;(color-theme-charcoal-black)
;(color-theme-black)
;(color-theme-billw)
;(color-theme-midnight)
;(color-theme-late-night)

;http://www.delorie.com/gnu/docs/emacs/emacs_465.html
;persistent buffers:
;The first time you save the state of the Emacs session, you must do it manually, with the command M-x desktop-save
;(desktop-load-default)
;(desktop-read)

; (setq mac-option-modifier 'meta)
; (setq mac-pass-option-to-system nil)

;(custom-set-faces
  ;; custom-set-faces was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
; '(default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 89 :width normal :foundry "unknown" :family "DejaVu Sans")))))

;uncomment the following on windows:
;(set-default-font "-outline-Consolas-normal-r-normal-normal-11-82-96-96-c-*-iso8859-1")

