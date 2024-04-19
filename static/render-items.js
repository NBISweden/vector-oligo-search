function renderItems(state, targetId, templateIds={}) {
  const {
    items,
    pageSize,
    selectedPage,
    viewType,
  } = state;
  defaultTemplateIds = {
    annotationTemplate: "annotation-template",
    rowTemplate: "row-template",
    paginationItemTemplate: "pagination-item-template",
    paginationTemplate: "pagination-template",
    listViewTemplate: "list-view-template",
  }
  templateIds = {
    ...defaultTemplateIds,
    ...templateIds,
  };
  const {
    annotationTemplate,
    rowTemplate,
    paginationItemTemplate,
    paginationTemplate,
    listViewTemplate,
  } = Object.keys(defaultTemplateIds).reduce((acc, templateKey) => {
    acc[templateKey] = getTemplate(templateIds[templateKey]);
    return acc;
  }, {});

  const pageCount = Math.ceil(items.length / pageSize);
  pageNumber = Math.min(pageCount - 1, selectedPage);
  const start = pageSize * pageNumber;
  const end = start + pageSize;
  const selectedItems = items.slice(start, end)
  
  const processedItems = selectedItems.map(
    (item, index) => ({
      ...item,
      index: index,
      annotatedView: item.annotations.map(annotation => (
        Mustache.render(
          annotationTemplate,
          {
            ...annotation,
            sequence: item.sequence.substring(
              annotation.position[0],
              annotation.position[1]
            )
          }
        )
      )).join("")
    })
  )

  const listItems = processedItems.map(item => Mustache.render(rowTemplate, item)).join("\n");
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

  const paginationView = Mustache.render(
    paginationTemplate,
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
        ].map((pagination) => (
          Mustache.render(
            paginationItemTemplate,
            pagination
          )
        )).join("")
      ),
      pageCount: pageCount
    }
  )
  const listView = Mustache.render(
    listViewTemplate,
    {
      paginationView,
      listItems
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
    {
      listViewTemplate: `${viewType}-list-view-template`,
      annotationTemplate: `${viewType}-annotation-template`,
      rowTemplate: `${viewType}-row-template`,
    }
  );
}
