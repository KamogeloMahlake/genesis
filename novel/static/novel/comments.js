const comments = document.getElementById('comments');
const hidden = comments.querySelector('input');

document.addEventListener('DOMContentLoaded', () => {
  createForm();
  loadComments(hidden.name, hidden.value, 1);
});


const createForm = () => {
  const form = document.createElement('form');
  form.style.border = '1px solid black';
  form.style.margin = '2rem';
  form.className = 'border-bottom p-3';
  form.innerHTML = `
    <h2>Add New Comment</a>
    <textarea class="form-control" rows="2"></textarea>
    <button type="submit" class="btn btn-primary d-flex mt-2">Add Comment</button>
`;
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    comments.removeChild(document.getElementById('comments-view'));
    fetch(`/compose/${hidden.name}`, {
      method: 'POST',
      body: JSON.stringify({
        text: form.querySelector('textarea').value,
        id: hidden.value
      })
    }).then(r => r.json()).then(d => {

        loadComments(hidden.name, hidden.value, 1);

        form.querySelector('textarea').value = "";
      })
  });

  comments.appendChild(form);
};

const loadComments = async (view, page_id, page_nr) => {
  const response = await fetch(`/comments/${view}/${page_id}/${page_nr}`);
  const data = await response.json();
  console.log(data.num);
  const div = document.createElement('div');
  div.id = "comments-view";
  data.comments.forEach(comment => {
    div.innerHTML += `<p>${comment.comment} <span>${comment.date}</span></p>`
  })
  div.appendChild(pageNav(data.current, data.num));
  comments.appendChild(div);
}

const pageNav = (current, numOfPages) => {
  const nav = document.createElement('nav');
  nav.ariaLabel = '...';
  const ul = document.createElement('ul');
  ul.className = 'pagination justify-content-center';
 
  numOfPages.forEach(p => {
    const li = document.createElement('li');
    li.className = p === current ? 'page-item active' : 'page-item';
    li.innerHTML = `<span class="page-link">${p}</span>`;
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => {
      loadComments(hidden.name, hidden.value, p);
      comments.removeChild(document.getElementById('comments-view'));
    });
    ul.appendChild(li);
  });

  nav.appendChild(ul);
  return nav;
};
