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

(tool-bar-mode -1) 

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

;;(autoload 'context)
(load-file "~/.emacs.d/context.el")

(add-hook 'text-mode-hook 'flyspell-mode) 

;http://www.emacswiki.org/cgi-bin/wiki/RecentFiles
(require 'recentf)
(recentf-mode 1)
;http://www.emacswiki.org/cgi-bin/wiki/Icicles
;need to investigate icicles

(load-file "~/.emacs.d/theme.el")

;keeping this around to undo the bad settings done elsewhere
(my-color-theme-light)

;; this works, but will probably be global for all instances
;; unless frame-setup overrides
(set-frame-height (selected-frame) 43)
(set-frame-width (selected-frame) 97)

;(name height width font)
;where height and width are for the frame
(frame-setup
 '(("blank" 29 98 '() ) ;; example
   ("drishti" 34 125 (default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 97 :width normal :foundry "unknown" :family "DejaVu Sans Mono")))) ) ;; my netbook
   ("context" 30 98 (default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 98 :width normal :foundry "unknown" :family "DejaVu Sans Mono")))) ) ;; my laptop
   ("breathe" 43 97 '(:height 43 :width 97) )
   )
)

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



;http://www.delorie.com/gnu/docs/emacs/emacs_465.html
;persistent buffers:
;The first time you save the state of the Emacs session, you must do it manually, with the command M-x desktop-save
;(desktop-load-default)
;(desktop-read)

;uncomment the following on windows:
;(set-default-font "-outline-Consolas-normal-r-normal-normal-11-82-96-96-c-*-iso8859-1")

;*2012.02.05 14:25:26 
;looking for a way to switch to only one window (in the emacs sense) open
;(one editing panel)
; this is what ctl-x 1 does
; but it must happen too early in the sequence (before other files are loaded)
; (delete-other-windows)

; this works:
(add-hook 'window-setup-hook 'delete-other-windows)
; via: 
; http://stackoverflow.com/questions/1144729/how-do-i-prevent-emacs-from-horizontally-splitting-the-screen-when-opening-multi

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(global-font-lock-mode t)
 '(inhibit-startup-screen t)
 '(tool-bar-mode nil))

(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
