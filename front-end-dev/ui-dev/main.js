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
$(".t-input").on("input", (e) => {
  clearTimeout(t_id);
  q = e.target.value;
  t_id = setTimeout(() => {
    fuse.then((f) => {
      s_res = f.search(q).slice(0, 10);
      $(".suggestions").empty();
      s_res.forEach((s) => {
        $(".suggestions").append(`
            <li class="suggestion-item">
                ${s.item.word}
            </li>
        `);
      });
    });
    console.log(s_res);
  }, 300);
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
