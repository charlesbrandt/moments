"
" vi configuration file
"
" nice resouce on how to edit this file:
" http://www.devdaily.com/unix/edu/un010003/
" 
" The ^M you see in is generated by typing a <CTRL-v> 
" (holding down the 'Ctrl' key and the 'v' key at the same time) 
" followed by a <CTRL-m>.
" 
" no blank lines!
:map #1 :0r!date "+*\%Y.\%m.\%d \%H:\%M:\%S"
"
" this will override the default behavior of j moving the cursor down 1 line:
:map j :0r!date "+*\%Y.\%m.\%d \%H:\%M:\%S"
"
" make a timestamp in place (similar to now function in emacs)
:map n :r!date "+*\%Y.\%m.\%d \%H:\%M:\%S"
