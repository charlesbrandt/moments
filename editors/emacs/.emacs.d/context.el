; put anything that you might want to reload here

;;this is how things were in python mode... those are stuck
;; always have comment region bound to a shortcut
(global-set-key "\C-c#" 'comment-region)

;; Journal Related functions:
(load-file "~/.emacs.d/journal.el")
(load-file "~/.emacs.d/programming.el")

;; reload .emacs
(defun reload ()
  (interactive)
  "Reload .emacs.d/context.el"
  ;(persistent-session-save-alist-to-file)
  (if (file-exists-p "~/.emacs.d/context.el")
      (load-file "~/.emacs.d/context.el"))
  
  ; these should be called by context
  ;(if (file-exists-p "~/.emacs.d/journal.el")
  ;    (load-file "~/.emacs.d/journal.el"))
  ;(if (file-exists-p "~/.emacs.d/programming.el")
  ;    (load-file "~/.emacs.d/programming.el"))
)

;  (if (file-exists-p "~/.emacs")
;      (load-file "~/.emacs")))

;*2009.12.27 17:49:12 
;(global-set-key (kbd "C-x r") 'search-backward)
;(global-set-key (kbd "C-r") 'revert-buffer)

; *2010.03.12 13:37:19 
; http://zhangda.wordpress.com/2009/04/13/hacking-on-revert-buffer/
; autorevert for log files
(setq revert-without-query (quote (".*20.*.txt")))
; regular expressions reference:
; http://www.cs.utah.edu/dept/old/texinfo/emacs18/emacs_17.html

;*2008.03.10 09:24 uncommenting:
;also [2007.11.01 13:50]
;(global-set-key (kbd "C-x w") 'browse-url-default-macosx-browser)
(setq-default browse-url-browser-function 'browse-url-firefox)
(setq-default browse-url-firefox-new-window-is-tab t)
(global-set-key (kbd "C-x w") 'browse-url-firefox)

