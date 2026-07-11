function Fish(id, w, h) {
  this.aspectratio = w / h;
  this.id = id;
  this.rounded = Math.random();
  this.saveable = typeof Blob === "function";
  this.width = w;
  this.height = h;

  var points, eye, patterns;
  var path = "";
  var colours = {
    c1: { bg: "#2254F4", text: "white" },
    c2: { bg: "#178CFF", text: "white" },
    c3: { bg: "#00B6FF", text: "white" },
    c4: { bg: "#08DEF9", text: "black" },
    c5: { bg: "#1DD3A7", text: "white" },
    c6: { bg: "#0DBC37", text: "white" },
    c7: { bg: "#67E767", text: "white" },
    c8: { bg: "#722EA5", text: "white" },
    c9: { bg: "#E6007C", text: "white" },
    c10: { bg: "#EF3AAB", text: "white" },
    c11: { bg: "#D73058", text: "white" },
    c12: { bg: "#D60303", text: "white" },
    c13: { bg: "#FF6700", text: "white" },
    c14: { bg: "#F9BC26", text: "black" },
  };

  function inRange(lo, hi) {
    return Math.min(Math.max(lo, Math.random()), hi);
  }
  function random(lo, hi) {
    return Math.random() * (hi - lo) + lo;
  }

  var _obj = this;

  this.size = function () {
    w = this.width;
    h = this.height;
    this.paper = new SVG(this.id, w, h);
    this.transform = {
      type: "scale",
      props: { x: w, y: h, cx: w, cy: h, r: w, "stroke-width": w },
    };
    return this;
  };
  this.resize = function () {
    this.size();
    this.paper.clear();
    this.draw();
    return this;
  };
  this.update = function () {
    this.create().draw();
  };
  this.create = function () {
    this.paper.clear();
    let c = "c" + Math.ceil(Math.random() * 14);
    this.colour = c;
    this.colour2 = colours[c].text;

    let front = inRange(0.1, 0.9);
    let head = random(0, 0.1);
    let back = inRange(0.1, 0.9);
    let tail = random(0, 0.05);
    let tailend = random(0.025, 0.05);
    let nose = random(-0.05, 0.05);

    points = new Array(10);
    patterns = [];

    // Start with nose
    points[0] = { x: 0.1 - nose, y: 0.5 - front * (Math.random() - 0.5) * 0.5 };
    points[1] = { x: points[0].x, y: points[0].y - front * Math.random() * 0.2 };

    // Slightly move top of nose forwards
    points[1].x -= (1 - Math.pow(front, 2)) * 0.02;

    // Add head
    points[2] = { x: 0.3 + head, y: (1 - front) / 2 };
    points[9] = { x: 0.3 + head, y: (1 + front) / 2 };

    // Add end of body
    points[3] = { x: 0.7, y: (1 - back) / 2 };
    points[8] = { x: 0.7, y: 0.75 + random(-0.15, 0.15) };

    // Add start of tail
    points[4] = { x: 0.83, y: 0.45 + tail };
    points[7] = { x: 0.83, y: 0.55 - tail };

    // Add end of tail
    points[5] = { x: 0.875 + tailend, y: 0.4 };
    points[6] = { x: 0.875 + tailend, y: 0.6 };

    eye = {
      x: points[0].x + (points[2].x - points[0].x) * 0.75,
      y: points[1].y - inRange(0, 0.6) * Math.abs(points[2].y - points[1].y),
    };

    if (Math.random() > 0.8)
      patterns.push({
        pattern: getPattern("belly"),
        attr: { "stroke-width": 0, stroke: "none", fill: this.colour2, opacity: 0.6 },
      });
    else {
      if (Math.random() > 0.9)
        patterns.push({
          pattern: getPattern("face"),
          attr: { "stroke-width": 0, stroke: "none", fill: "black", opacity: 0.7 },
        });
      if (Math.random() > 0.7)
        patterns.push({
          pattern: getPattern("stripes"),
          attr: { "stroke-width": 0.02, stroke: this.colour2, fill: this.colour2, opacity: 0.6 },
        });
      else {
        if (Math.random() > 0.7)
          patterns.push({
            pattern: getPattern("lines"),
            attr: { "stroke-width": 0.01, stroke: this.colour2, fill: this.colour2, opacity: 0.6 },
          });
        else {
          if (Math.random() > 0.7)
            patterns.push({
              circles: getPattern("circles"),
              attr: { "stroke-width": 0.008, stroke: this.colour2, fill: "none", opacity: 0.8 },
            });
        }
      }
    }

    return this;
  };
  this.save = function () {
    if (
      typeof Blob !== "function" ||
      typeof document === "undefined" ||
      typeof window === "undefined"
    ) {
      console.log(this.svg);
      return this;
    }

    var textFileAsBlob = new Blob([this.svg], { type: "text/application/svg+xml" });
    var fileNameToSaveAs = "fish.svg";

    function destroyClickedElement(event) {
      document.body.removeChild(event.target);
    }
    var dl = document.createElement("a");
    dl.download = fileNameToSaveAs;
    dl.innerHTML = "Download File";
    if (window.webkitURL != null) {
      // Chrome allows the link to be clicked
      // without actually adding it to the DOM.
      dl.href = window.webkitURL.createObjectURL(textFileAsBlob);
    } else {
      // Firefox requires the link to be added to the DOM
      // before it can be clicked.
      dl.href = window.URL.createObjectURL(textFileAsBlob);
      dl.onclick = destroyClickedElement;
      dl.style.display = "none";
      document.body.appendChild(dl);
    }
    dl.click();
    return this;
  };
  this.draw = function () {
    let i, dx, dy, dy2;

    // Move to start
    path = [["M", [Math.round(w * points[0].x), Math.round(h * points[0].y)]]];
    let bodygrad1 = (points[3].y - points[2].y) / (points[3].x - points[2].x);
    let bodygrad2 = (points[9].y - points[8].y) / (points[9].x - points[8].x);

    for (i = 0; i <= points.length; i++) {
      if (i == 2) {
        dx = -0.2 * this.rounded;
        dy = bodygrad1 * dx;
        dy2 = Math.abs(points[2].y - points[1].y);
        if (dy2 < 0.15) {
          dx *= 0.5;
          dy *= 0.5;
        } else if (dy2 < 0.05) {
          dx = 0;
          dy = 0;
        }
        path.push([
          "C",
          [
            Math.round(w * points[i - 1].x),
            Math.round(h * points[i - 1].y),
            Math.round(w * (points[i].x + dx)),
            Math.round(h * (points[i].y + dy)),
            Math.round(w * points[i].x),
            Math.round(h * points[i].y),
          ],
        ]);
      } else if (i == 4) {
        dx = 0.1 * this.rounded;
        dy = bodygrad1 * dx;
        path.push([
          "C",
          [
            Math.round(w * (points[i - 1].x + dx)),
            Math.round(h * (points[i - 1].y + dy)),
            Math.round(w * points[i].x),
            Math.round(h * points[i].y),
            Math.round(w * points[i].x),
            Math.round(h * points[i].y),
          ],
        ]);
      } else if (i == 8) {
        dx = 0.1 * this.rounded;
        dy = bodygrad2 * dx;
        path.push([
          "C",
          [
            Math.round(w * points[i - 1].x),
            Math.round(h * points[i - 1].y),
            Math.round(w * (points[i].x + dx)),
            Math.round(h * (points[i].y + dy)),
            Math.round(w * points[i].x),
            Math.round(h * points[i].y),
          ],
        ]);
      } else if (i == 10) {
        dx = -0.15 * this.rounded;
        dy = bodygrad2 * dx;
        if (Math.abs(points[0].y - points[9].y) < 0.05) {
          dx = 0;
          dy = 0;
        }
        path.push([
          "C",
          [
            Math.round(w * (points[i - 1].x + dx)),
            Math.round(h * (points[i - 1].y + dy)),
            Math.round(w * points[0].x),
            Math.round(h * points[0].y),
            Math.round(w * points[0].x),
            Math.round(h * points[0].y),
          ],
        ]);
      } else {
        path.push(["L", [Math.round(w * points[i].x), Math.round(h * points[i].y)]]);
      }
    }
    this.paper.rect(0, 0, w, h, 0).attr({ fill: "#0000F4", stroke: "none" });
    this.paper.clip({ type: "path", path: path, id: "fish" });
    this.paper
      .path(path)
      .attr({ stroke: "none", fill: colours[this.colour].bg, "clip-path": "shape" });

    if (patterns.length > 0) {
      for (i = 0; i < patterns.length; i++) {
        patterns[i].attr["clip-path"] = "fish";
        if (patterns[i].pattern) {
          this.paper.path(patterns[i].pattern).attr(patterns[i].attr).transform(this.transform);
        } else if (patterns[i].circles) {
          for (var c = 0; c < patterns[i].circles.length; c++)
            this.paper
              .circle(
                patterns[i].circles[c].cx,
                patterns[i].circles[c].cy,
                patterns[i].circles[c].r,
              )
              .attr(patterns[i].attr)
              .transform(this.transform);
        }
      }
    }
    this.paper
      .circle(eye.x, eye.y, 0.02)
      .attr({ stroke: "none", fill: "white" })
      .transform(this.transform);
    this.paper
      .circle(eye.x, eye.y, 0.015)
      .attr({ stroke: "none", fill: "black" })
      .transform(this.transform);
    this.paper.draw();

    this.svg = this.paper.canvas.innerHTML;

    // Update text of button when a DOM is available
    if (this.saveable && typeof getEl === "function") {
      var saveEl = getEl("#save");
      if (saveEl)
        saveEl.innerHTML = '<span class="line">S</span>ave SVG (' + niceSize(this.svg.length) + ")";
    }

    return this;
  };
  function niceSize(b) {
    if (b > 1e12) return (b / 1e12).toFixed(2) + " TB";
    if (b > 1e9) return (b / 1e9).toFixed(2) + " GB";
    if (b > 1e6) return (b / 1e6).toFixed(2) + " MB";
    if (b > 1e3) return (b / 1e3).toFixed(2) + " kB";
    return b + " bytes";
  }

  function getPattern(t) {
    let str = "";
    let x, y, dx, dy, x2, r, n, sep, i, j, tall, f;
    if (t == "stripes") {
      r = Math.random();
      n = Math.max(3, Math.round(Math.random() * 6));
      sep = 0.04;
      var angle = Math.random() * 0.25;
      var half = Math.random() > 0.5 ? true : false;
      tall = half ? 1 / 2 : 1;
      dy = sep * Math.cos(angle) * Math.sin(angle);
      for (i = 0, x = points[2].x; i < n; i++, x += sep) {
        str +=
          "M" + x.toFixed(2) + ",0l" + (tall * Math.tan(angle)).toFixed(2) + "," + tall.toFixed(2);
        tall -= dy;
      }
      if (half) {
        for (i = 0, x = points[3].x; i < n; i++, x -= sep) {
          str +=
            "M" +
            x.toFixed(2) +
            "," +
            h.toFixed(2) +
            "l-" +
            (tall * Math.tan(angle)).toFixed(2) +
            ",-" +
            tall.toFixed(2);
          tall -= dy;
        }
      }
      return str;
    } else if (t == "lines") {
      r = Math.random();
      n = Math.max(5, Math.round(Math.random() * 20));
      dy = 0.03 * 1;
      tall = 0.5 + random(0, 0.4);
      for (i = 0; i < n; i++) {
        x = points[2].x + random(0, 0.1);
        while (x < points[3].x) {
          dx = Math.random() * (points[3].x - points[2].x);
          x2 = Math.min(x + dx, points[4].x) - x;
          str += "M" + x.toFixed(2) + "," + tall.toFixed(2) + "l" + x2.toFixed(2) + ",0";
          x += dx + 0.02;
        }
        tall -= dy;
      }
      return str;
    } else if (t == "circles") {
      r = random(0.04, 0.06);
      var circles = [];
      f = r * 2 * Math.cos((Math.PI * 30) / 180);
      x = points[2].x - r / 2;
      for (i = 0; i < (points[3].x - points[2].x) / (r * 2); i++) {
        x += f;
        y = points[2].y - (r - (i % 2 == 0 ? r : 0)) * (w / h);
        for (j = 0; j < (points[9].y - points[3].y) / (r * 2); j++) {
          y += r * 2 * (w / h);
          if (Math.random() > 0.1) circles.push({ cx: x, cy: y, r: r });
        }
      }
      return circles;
    } else if (t == "belly") {
      return "M0,1L" + points[2].x + ",0.5L1,0.5L1,1Z";
    } else if (t == "face") {
      return "M0,0L" + points[2].x + ",0l0,1L0,1Z";
    } else {
      return "";
    }
  }

  this.size();

  return this;
}

function SVG(id, width, height) {
  if (!id) return this;
  this.canvas = { innerHTML: "" };
  this.w = width;
  this.h = height;

  this.canvas.innerHTML =
    '<svg height="' +
    this.h +
    '" version="1.1" width="' +
    this.w +
    '" viewBox="0 0 ' +
    this.w +
    " " +
    this.h +
    '" xmlns="http://www.w3.org/2000/svg"><desc>Created by stuQuery SVG</desc></svg>';

  // Initialise
  this.nodes = [];
  this.clippaths = [];

  function Path(path) {
    this.path = path;
    this.p = path;

    if (typeof path === "string") {
      this.path = path;
      this.p = path;
      var c;
      this.p += "0";
      this.p = this.p.match(/(^|[A-Za-z]| )[^ A-Za-z]+/g);
      var a = this.p[this.p.length - 1];
      this.p[this.p.length - 1] = a.substring(0, a.length - 1);
      for (var i = 0; i < this.p.length; i++) {
        if (this.p[i].search(/[A-Za-z]/) == 0) {
          c = this.p[i][0];
          this.p[i] = this.p[i].substr(1);
        } else {
          if (this.p[i][0] == " ") this.p[i] = this.p[i].substr(1);
          c = "";
        }
        this.p[i] = [c, this.p[i].split(/\,/)];
        if (this.p[i][1].length == 2) {
          for (var j = 0; j < this.p[i][1].length; j++)
            this.p[i][1][j] = parseFloat(this.p[i][1][j]);
        } else {
          this.p[i][1] = [];
        }
      }
    } else {
      this.p = path;
      this.path = this.string(path);
    }
    return this;
  }
  Path.prototype.string = function () {
    var str = "";
    for (var i = 0; i < this.p.length; i++) {
      str +=
        (this.p[i][0] ? this.p[i][0] : " ") +
        (this.p[i][1].length > 0 ? this.p[i][1].join(",") : " ");
    }
    return str;
  };
  function copy(o) {
    var out, v, key;
    out = Array.isArray(o) ? [] : {};
    for (key in o) {
      v = o[key];
      out[key] = typeof v === "object" ? copy(v) : v;
    }
    return out;
  }
  Path.prototype.copy = function () {
    return new Path(copy(this.p));
  };
  function Node(inp) {
    let i;
    this.transforms = [];
    // Make a structure to hold the original properties
    this.orig = {};
    for (i in inp) this[i] = inp[i];
    for (i in inp) this.orig[i] = inp[i];
    if (this.path) {
      this.path = new Path(this.path);
      this.d = this.path.string();
      this.orig.path = this.path.copy();
      this.orig.d = this.d;
    }
    return this;
  }
  Node.prototype.attr = function (a) {
    this.attributes = a;
    this.orig.attributes = JSON.parse(JSON.stringify(a));
    return this;
  };
  Node.prototype.transform = function (ts) {
    if (typeof ts.length === "undefined" && typeof ts === "object") ts = [ts];
    if (!this.transforms) this.transforms = [];
    for (var t = 0; t < ts.length; t++) this.transforms.push(ts[t]);
    return this;
  };
  Node.prototype.update = function () {
    let t, p, i, j;
    //console.log('update',this.type,this.transforms)
    if (this.transforms && this.transforms.length > 0) {
      // Reset path
      if (this.orig.path) this.path = this.orig.path.copy();

      // Loop over all the transforms and update properties
      for (t = 0; t < this.transforms.length; t++) {
        for (p in this.transforms[t].props) {
          // Replace the current value with the original
          if (this.orig[p] && this[p]) this[p] = JSON.parse(JSON.stringify(this.orig[p]));
        }
      }
      // Update attributes to the original ones
      if (this.orig.attributes) this.attributes = JSON.parse(JSON.stringify(this.orig.attributes));

      for (t = 0; t < this.transforms.length; t++) {
        if (this.transforms[t].type == "scale") {
          if (this.type == "path") {
            for (i = 0; i < this.orig.path.p.length; i++) {
              for (j = 0; j < this.orig.path.p[i][1].length; j++) {
                this.path.p[i][1][j] *= this.transforms[t].props[j % 2 == 0 ? "x" : "y"];
              }
            }
            this.path.path = this.path.string();
            this.d = this.path.path;
          } else {
            for (p in this.transforms[t].props) {
              if (this[p]) this[p] *= this.transforms[t].props[p];
            }
          }
          if (this.attributes) {
            for (p in this.transforms[t].props) {
              if (this.attributes[p]) this.attributes[p] *= this.transforms[t].props[p];
            }
          }
        }
      }
    }
    return this;
  };
  this.circle = function (x, y, r) {
    this.nodes.push(new Node({ cx: x, cy: y, r: r, type: "circle" }));
    return this.nodes[this.nodes.length - 1];
  };
  this.rect = function (x, y, w, h, r) {
    this.nodes.push(
      new Node({ x: x, y: y, width: w, height: h, r: r, rx: r, ry: r, type: "rect" }),
    );
    return this.nodes[this.nodes.length - 1];
  };
  this.path = function (path) {
    this.nodes.push(new Node({ path: path, type: "path" }));
    return this.nodes[this.nodes.length - 1];
  };
  this.clip = function (o) {
    this.clippaths.push(new Node(o));
    return this.clippaths[this.clippaths.length - 1];
  };

  return this;
}
SVG.prototype.clear = function () {
  this.nodes = [];
  this.clippaths = [];
  this.draw();
  return this;
};
SVG.prototype.draw = function () {
  let dom =
    '<svg height="' +
    this.h +
    '" version="1.1" width="' +
    this.w +
    '" viewBox="0 0 ' +
    this.w +
    " " +
    this.h +
    '" xmlns="http://www.w3.org/2000/svg">';
  let i, j, a;

  dom += "<desc>Created by stuQuery SVG</desc>";

  if (this.clippaths.length > 0) {
    dom += "<defs>";
    for (i = 0; i < this.clippaths.length; i++) {
      dom += '<clipPath id="' + this.clippaths[i].id + '">';
      if (this.clippaths[i].type) {
        // Update node with any transforms
        this.clippaths[i].update();
        dom += "<" + this.clippaths[i].type;
        // Add properties
        for (j in this.clippaths[i]) {
          if (
            j != "type" &&
            j != "id" &&
            typeof this.clippaths[i][j] !== "object" &&
            typeof this.clippaths[i][j] !== "function" &&
            j != "attributes"
          ) {
            dom += " " + j + '="' + this.clippaths[i][j] + '"';
          }
        }
        dom += " />";
      }
      dom += "</clipPath>";
    }
    dom += "</defs>";
  }

  for (i = 0; i < this.nodes.length; i++) {
    if (this.nodes[i].type) {
      dom += "<" + this.nodes[i].type;
      // Update node with any transforms
      this.nodes[i].update();
      // Add properties
      for (j in this.nodes[i]) {
        if (
          j != "type" &&
          typeof this.nodes[i][j] !== "object" &&
          typeof this.nodes[i][j] !== "function" &&
          j != "attributes"
        )
          dom += " " + j + '="' + this.nodes[i][j] + '"';
      }
      // Add attributes
      for (a in this.nodes[i].attributes) {
        dom +=
          " " +
          a +
          '="' +
          (a == "clip-path" ? "url(#" : "") +
          this.nodes[i].attributes[a] +
          (a == "clip-path" ? ")" : "") +
          '"';
      }
      dom += " />";
    }
  }
  dom += "</svg>";
  this.canvas.innerHTML = dom;
  return this;
};

var fish;
fish = new Fish("fish", 64, 64);
fish.update();
console.log(fish.svg);
