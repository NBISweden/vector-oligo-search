function parsePaginationState(state) {
  const {
    items,
    pageSize,
    selectedPage,
  } = state;
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
          pageNumber: pn,
          active: pn === pageNumber ? "active" : ""
        } : {
          disabled: "disabled",
        }
      )
    }
  }

  return {
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
    pageCount,
    currentPageNumber: pageNumber,
    pageSize: pageSize,
  }
}

function parseViewState(state) {
  const {viewType, viewTypes} = state;
  return {
    viewTypes: viewTypes.map(vt => ({
      ...vt,
      active: viewType === vt.id ? "active" : "",
    })),
    viewType,
  }
}

function renderView(state, targetId, templateId="table-list-view-template") {
  const template = getTemplate(templateId);
  const view = Mustache.render(
    template,
    state
  )
  document.getElementById(targetId).innerHTML = view;
}

function getTemplate(templateId) {
  try {
    return document.getElementById(templateId).innerHTML.trim();
  } catch (e) {
    throw new Error(`Unable to load template with id "${templateId}"`)
  }
}

function getPaginator(items) {
  return function() {
    const queryString = window.location.hash.replace("#", "");
    const urlParams = new URLSearchParams(queryString);
    const viewTypes = [
      {id: "accordion", icon: "bi-view-stacked", name: "Accordion"},
      {id: "table", icon: "bi-table", name: "Table"}
    ]
    const viewType = urlParams.get("view") || "accordion";
    const selectedPage = urlParams.get("page") || 0;
    const pageSize = Math.max(urlParams.get("pageSize") || 12, 6);
    const paginationState = parsePaginationState({items, pageSize, selectedPage});
    const viewState = parseViewState({viewType, viewTypes})
    renderView(
      {
        ...paginationState,
        ...viewState,
      },
      "item-view",
      `${viewType}-list-view-template`
    )
    renderView(
      {
        ...paginationState,
        ...viewState,
      },
      "view-type-view",
      "view-type-view-template"
    )
  }
}
