function renderItems(state, targetId, templateId="table-list-view-template") {
  const {
    items,
    pageSize,
    selectedPage,
    viewType,
  } = state;
  const listViewTemplate = getTemplate(templateId);

  const pageCount = Math.ceil(items.length / pageSize);
  pageNumber = Math.min(pageCount - 1, selectedPage);
  const start = pageSize * pageNumber;
  const end = start + pageSize;
  const listItems = items.slice(start, end).map(
    (item, index) => ({
      ...item,
      index: index,
      annotations: item.annotations.map(
        annotation => ({
          ...annotation,
          sequence: item.sequence.substring(
            annotation.position[0],
            annotation.position[1]
          )
        })
      )
    })
  )

  const maxListedPages = 5;
  const pageGroupStart = Math.floor(pageNumber / maxListedPages) * maxListedPages;
  const listedPages = Math.min(pageCount, maxListedPages);

  function inPageRange(pn) {
    return pn >= 0 && pn < pageCount;
  }

  function paginationPage(pn, label) {
    return {
      label: label,
      ...(
        inPageRange(pn) ? {
          href: `#?page=${pn}&pageSize=${pageSize}&view=${viewType}`,
          active: pn === pageNumber ? "active" : ""
        } : {
          disabled: "disabled",
        }
      )
    }
  }

  const listView = Mustache.render(
    listViewTemplate,
    {
      paginationItems: (
        [
          paginationPage(pageGroupStart - listedPages, "<<"),
          paginationPage(pageNumber - 1, "Previous"),
          ...Array.from({length: listedPages}).map((_, index) => (
            paginationPage(pageGroupStart + index, pageGroupStart + index + 1)
          )),
          paginationPage(pageNumber + 1, "Next"),
          paginationPage(pageGroupStart + listedPages, ">>"),
        ]
      ),
      listItems,
      pageCount
    }
  )
  document.getElementById(targetId).innerHTML = listView;
}

function getTemplate(templateId) {
  try {
    return document.getElementById(templateId).innerHTML.trim();
  } catch (e) {
    throw new Error(`Unable to load template with id "${templateId}"`)
  }
}

function updatePageState() {
  const queryString = window.location.hash.replace("#", "");
  const urlParams = new URLSearchParams(queryString);
  const viewType = {
    "base": "accordion",
    "table": "table"
  }[urlParams.get("view")] || "accordion";
  const selectedPage = urlParams.get("page") || 0;
  const pageSize = Math.max(urlParams.get("pageSize") || 12, 6);
  renderItems(
    {items, pageSize, selectedPage, viewType},
    "item-view",
    `${viewType}-list-view-template`
  );
}
