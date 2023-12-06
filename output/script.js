/**
 * Toggle "opt-hidden" elements with a button (this).
 * Scroll back to button when the list reduces in height.
 */
function showMore() {
  const ul = this.previousElementSibling;
  var showingMore = false;
  
  Array.from(ul.children).forEach(c => {
    if (c.classList.contains("opt-hidden")) {
      if (c.getAttribute("hidden")) {
        c.removeAttribute("hidden");
        this.innerHTML = this.innerHTML.replace("More", "Fewer");
        showingMore = true;
      } else {
        c.setAttribute("hidden", null);
        this.innerHTML = this.innerHTML.replace("Fewer", "More");
        showingMore = false;
      }
    }
  });

  if (!showingMore) {
    const topOfList = ul.getBoundingClientRect().top
    if (topOfList < 0) {
      const absoluteTopOfList = ul.getBoundingClientRect().top + window.scrollY;
      console.log(absoluteTopOfList - 50);
      window.scrollTo({
        top: absoluteTopOfList - 50,
        behavior: "smooth"
      });
    }
  }
}

function convertRemToPixels(rem) {    
    return rem * parseFloat(getComputedStyle(document.documentElement).fontSize);
}

window.addEventListener("load", () => {
  const vw = Math.max(
    document.documentElement.clientWidth || 0,
    window.innerWidth || 0
  );
  const isMobile = vw <= convertRemToPixels(40);
  const visibleArticleCount = 4;
  const visibleBillCount = isMobile ? 4 : 10;

  // Hook up buttons
  document.querySelectorAll("button.show-more").forEach((btn) => {
    btn.addEventListener("click", showMore);
  });


  // Hide a number of elements to be shown again
  const billList = document.querySelector(".bill-list");
  const newsArticleLists = document.querySelectorAll(".news-article-list");

  // Bill list
  var countBillHidden = 0;
  Array.from(billList.children).forEach((c, index) => {
    if (index >= visibleBillCount) {
      c.classList.add("opt-hidden");
      c.setAttribute("hidden", null);
      countBillHidden++;
    }
  });
  billList
    .parentElement
    .querySelector("button.show-more")
    .innerHTML = "Show More (" + String(countBillHidden) + ")";

  // Each news article list
  newsArticleLists.forEach(list => {
    var countArticleHidden = 0;
    Array.from(list.children).forEach((c, index) => {
      if (index >= visibleArticleCount) {
        c.classList.add("opt-hidden");
        c.setAttribute("hidden", null);
        countArticleHidden++;
      }
    })
    list
      .parentElement
      .querySelector("button.show-more")
      .innerHTML = "Show More (" + String(countArticleHidden) + ")";
  })
});
