/*
  Copyright (c) 2011 Cameron McEfee

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

(function(a){var d=[],f=a(window).width(),g=a(window).height();a(window).resize(function(){f=a(window).width();g=a(window).height()});a.fn.plaxify=function(h){return this.each(function(){var b={xRange:0,yRange:0,invert:!1},c;for(c in h)b[c]==0&&(b[c]=h[c]);b.obj=a(this);b.startX=this.offsetLeft;b.startY=this.offsetTop;b.invert==!1?(b.startX-=Math.floor(b.xRange/2),b.startY-=Math.floor(b.yRange/2)):(b.startX+=Math.floor(b.xRange/2),b.startY+=Math.floor(b.yRange/2));d.push(b)})};a.plax={enable:function(){a(document).bind("mousemove.plax",
function(a){var b=Math.round(a.pageX/f*100)/100,a=Math.round(a.pageY/g*100)/100,c,e;for(e=d.length;e--;)c=d[e],c.invert!=!0?c.obj.css("left",c.startX+c.xRange*b).css("top",c.startY+c.yRange*a):c.obj.css("left",c.startX-c.xRange*b).css("top",c.startY-c.yRange*a)})},disable:function(){a(document).unbind("mousemove.plax")}};typeof ender!=="undefined"&&a.ender(a.fn,!0)})(function(){return typeof jQuery!=="undefined"?jQuery:ender}());
