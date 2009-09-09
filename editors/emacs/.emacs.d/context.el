;;this is how things were in python mode... those are stuck
;; always have comment region bound to a shortcut
(global-set-key "\C-c#" 'comment-region)

;; Journal Related functions:
(load-file "~/.emacs.d/journal.el")

;; reload .emacs
(defun reload ()
  (interactive)
  "Reload .emacs.d/context.el"
  ;(persistent-session-save-alist-to-file)
  (if (file-exists-p "~/.emacs.d/context.el")
      (load-file "~/.emacs.d/context.el")
      (load-file "~/.emacs.d/journal.el"))
)
;  (if (file-exists-p "~/.emacs")
;      (load-file "~/.emacs")))

;*2008.03.10 09:24 uncommenting:
;also [2007.11.01 13:50]
;(global-set-key (kbd "C-x w") 'browse-url-default-macosx-browser)
(setq-default browse-url-browser-function 'browse-url-firefox)
(setq-default browse-url-firefox-new-window-is-tab t)
(global-set-key (kbd "C-x w") 'browse-url-firefox)

;============================
; Programming MODES
;============================
;PYTHON
(setq auto-mode-alist (cons '("\\.py$" . python-mode) auto-mode-alist))
(setq interpreter-mode-alist (cons '("python" . python-mode) interpreter-mode-alist))
(autoload 'python-mode "python-mode" "Python editing mode." t)

(add-to-list 'auto-mode-alist '("\\.zpt$" . html-mode))
(add-to-list 'auto-mode-alist '("\\.pt$" . html-mode))
(add-to-list 'auto-mode-alist '("\\.dtml$" . html-mode))
(add-to-list 'auto-mode-alist '("\\.mako$" . html-mode))

;call any other programming modes you need here:
(load-file "~/.emacs.d/programming.el")
