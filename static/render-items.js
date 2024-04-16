function renderItems(items, pageSize, pageNumber, targetId) {
  const pageCount = Math.ceil(items.length / pageSize);
  pageNumber = Math.min(pageCount - 1, pageNumber);
  const start = pageSize * pageNumber;
  const end = start + pageSize;
  const selectedItems = items.slice(start, end)
  const annotationTemplate = (
`<span class="annotated-sequence break-all" data-annotation="{{ label }}">{{ sequence }}</span>`
  )
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

  const rowTemplate = (
`<div class="row my-lg-5 my-sm-2">
  <h3>{{ gene_id }}</h3>
  <div class="accordion" id="accordion-{{ index }}">
    <div class="accordion-item">
      <h4 class="accordion-header">
        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-annotated-{{ index }}" aria-expanded="true" aria-controls="collapse-annotated-{{ index }}">
          Annotated sequence
        </button>
      </h4>
      <div id="collapse-annotated-{{ index }}" class="accordion-collapse collapse show" data-bs-parent="#accordion-{{ index }}">
        <div class="accordion-body">
          <p>
            {{{annotatedView}}}
          </p>
        </div>
      </div>
    </div>
    <div class="accordion-item">
      <h4 class="accordion-header">
        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-sequence-{{ index }}" aria-expanded="true" aria-controls="collapse-sequence-{{ index }}">
          Sequence only
        </button>
      </h4>
      <div id="collapse-sequence-{{ index }}" class="accordion-collapse collapse" data-bs-parent="#accordion-{{ index }}">
        <div class="accordion-body">
          <p>
            <span class="annotated-sequence break-all" data-annotation="Oligo sequence">{{ sequence }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</div>`
  );
  const pageView = processedItems.map(item => Mustache.render(rowTemplate, item)).join("\n");
  const maxListedPages = 5;
  const pageGroupStart = Math.floor(pageNumber / maxListedPages) * maxListedPages;
  const listedPages = Math.min(pageCount, maxListedPages);
  const paginationItemTemplate = (
`<li class="page-item {{disabled}}"><a class="page-link {{active}}" href="{{href}}">{{label}}</a></li>`
  );
  const paginationTemplate = (
`<nav aria-label="Page navigation">
  <ul class="pagination justify-content-center">
    {{{paginationItems}}}
    <li class="page-item"><span class="pagination-label"> of {{pageCount}} pages.</span></li>
  </ul>
</nav>`
  );

  function inPageRange(pn) {
    return pn >= 0 && pn < pageCount;
  }

  function paginationPage(pn, label) {
    return {
      label: label,
      ...(
        inPageRange(pn) ? {
          href: `#?page=${pn}&pageSize=${pageSize}`,
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
  document.getElementById(targetId).innerHTML = [paginationView, pageView, paginationView].join("\n");
}

function updatePageState() {
  const queryString = window.location.hash.replace("#", "");
  const urlParams = new URLSearchParams(queryString);
  const selectedPage = urlParams.get("page") || 0;
  const pageSize = Math.max(urlParams.get("pageSize") || 12, 6);
  renderItems(items, pageSize, selectedPage, "item-view");
}
