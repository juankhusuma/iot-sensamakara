import "./style.css";
import $ from "jquery";
import Fuse from "fuse.js";

const fuse = (async () => {
  const res = await fetch("/words.json");
  const data = await res.json();
  return new Fuse(data, { keys: ["word"] });
})();

let q;
let t_id;
let s_res = [];
let sel = -1;

$(document).bind("contextmenu", function (e) {
  return false;
});

$(".t-input").on("input", (e) => {
  clearTimeout(t_id);
  q = e.target.value;
  t_id = setTimeout(() => {
    fuse.then((f) => {
      s_res = f.search(q).slice(0, 10);
      $(".suggestions").empty();
      s_res.forEach((s, i) => {
        $(".suggestions").append(`
            <li class="suggestion-item" id="${i}">
                ${s.item.word}
            </li>
        `);
      });
    });
    console.log(s_res);
  }, 300);
});

$(window).on("mousedown", (e) => {
  if (e.button === 1) {
    sel = (sel + 1) % s_res.length;
    $(".suggestion-item").css("color", "white");
    $(`#${sel}`).css("color", "blue");
  }
  if (e.button === 2) {
    e.preventDefault();
    const i = document.getElementById("char");
    i.innerHTML += $(`#${sel}`).text().trim() + " ";
    $(".t-input").val("");
    sel = -1;
  }
});

$(document).ready(() => {
  setTimeout(() => {
    $(".loader").css("opacity", "0");
    setTimeout(() => {
      $(".content").fadeTo(200, 1);
      $(".loader").css("display", "none");
    }, 2000);
  }, 500);
});
