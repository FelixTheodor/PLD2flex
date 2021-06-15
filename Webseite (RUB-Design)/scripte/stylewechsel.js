/* 
 Onload 
*/ 
window.onload = initCSS; 

// initCSS: If there's a "mystyle" cookie, set the active stylesheet when the page loads 
function initCSS() { 
 var style = readCookie("mystyle"); 
 if (style) { 
 activeCSS(style); 
 } 
} 
/* 
 Switcher functions 
*/ 
// activeCSS: Set the active stylesheet 
function activeCSS(title) { 
 
 var i, oneLink; 
 for (i = 0; (oneLink = document.getElementsByTagName("link")[i]); i++) { 
 if (oneLink.getAttribute("title") && findWord("stylesheet", oneLink.getAttribute("rel"))) { 
 oneLink.disabled = true; 
 if (oneLink.getAttribute("title") == title) { 
 oneLink.disabled = false; 
 } 
 } 
 } 
 setCookie("mystyle", title, 365); 
} 
// findWord: Used to find a full word (needle) in a string (haystack) 
function findWord(needle, haystack) { 
 var init = needle + "\\b"; 
 return haystack.match(needle + "\\b"); 
} 
/* 
 Cookie functions 
*/ 
// Set the cookie 
function setCookie(name,value,days) { 
 if (days) { 
 var date = new Date(); 
 date.setTime(date.getTime()+(days*24*60*60*1000)); 
 var expires = ";expires="+date.toGMTString(); 
 } else { 
 expires = ""; 
 } 
 document.cookie = name+"="+value+expires+";"; 
} 
// Read the cookie 
function readCookie(name) { 
 var needle = name + "="; 
 var cookieArray = document.cookie.split(';'); 
 for(var i=0;i < cookieArray.length;i++) { 
 var pair = cookieArray[i]; 
 while (pair.charAt(0)==' ') { 
 pair = pair.substring(1, pair.length); 
 } 
 if (pair.indexOf(needle) == 0) { 
 return pair.substring(needle.length, pair.length); 
 } 
 } 
 return null; 
} 


/* Bildwechsel */
Erstlogo = new Image(102, 102);
Erstlogo.src = "http://www.ruhr-uni-bochum.de/images/logo/logo-rub-102.gif";
Zweitlogo = new Image(102, 102);
Zweitlogo.src = "http://www.ruhr-uni-bochum.de/images/logo/logo-rub-102-invers.gif";
Erstschrift = new Image(237, 18);
Erstschrift.src = "http://www.ruhr-uni-bochum.de/images/logo/rub-schriftzug.gif";
Zweitschrift = new Image(237, 18);
Zweitschrift.src = "http://www.ruhr-uni-bochum.de/images/logo/rub-schriftzug-invers.gif";

function Logowechsel() {
  document.images['rublabel'].src = Erstlogo.src;
  document.images['schriftzug'].src = Erstschrift.src;
}
function Logowechselinvers() {
  document.images['rublabel'].src = Zweitlogo.src;
  document.images['schriftzug'].src = Zweitschrift.src;
}

