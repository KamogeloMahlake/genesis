function Form({onSubmit, buttonText, onChange, value}) {
  return (
    <form onSubmit={onSubmit} style={{border: '1px solid black', margin: '2rem'}} className="border-bottom p-3">
      <textarea className="form-control" rows="2" onChange={onChange} value={value}></textarea>
      <button type="submit" className="btn btn-primary d-flex mt-2">{buttonText}</button>     
    </form>
  )
}

function AddNewComment({handleTextChange, handleSubmit, value}) {
  return (
    <div>
      <h2 style={{textAlign: "center"}}>Add New Comment</h2>
      <Form 
      value={value}
      onChange={handleTextChange}
      onSubmit={handleSubmit} 
      buttonText="Add Comment" />
    </div>
  )
}

function CommentText({comment}) {
  const html = comment.split('\n').map((line, index) => (
    <p key={index}>{line}</p>
  ));
  return (
    <div>
      {html}
    </div>
  );
}
function Comment({userName, image, comment, date, user, likesCount, liked, id, disliked, dislikesCount, load, replies}) {
  const [s, setS] = React.useState({
    showForm: false,
    text: "",
    showReplies: false
  });
  
  const handleLike = (e) => {
    if (!user) return;
    e.preventDefault();
    console.log(id);
    console.log(e.target);
    console.log(e.target.name);
    fetch(`/like/${id}`)
    .then(r => r.json())
    .then(d => {
      load();
    })
    .catch(e => console.log(e));
  };

  const handleDislike = (e) => {
    if (!user) return;
    e.preventDefault();
    fetch(`/dislike/${id}`)
    .then(r => r.json())
    .then(d => {
      load();
    })
    .catch(e => console.log(e));
  };
  
  const submitReply = (e) => {
    e.preventDefault();
    if (!user) return;
    if (s.text.length === 0) return;
    fetch(`/reply/${id}`, {
      method: 'POST',
      body: JSON.stringify({
        text: s.text,
      })
    })
    .then(r => r.json())
    .then(d => {
      setS({
        text: '',
        showForm: false
      });
      load();
      console.log(d);
      console.log(s);
    })
    .catch(e => console.log(e));
  }
  const showRepliesForm = e => {
    setS({...s, showForm: !s.showForm});
  }

  return (
    <div className="list-group-item list-group-item-action">
      <div className="d-flex w-100 justify-content-between">
        <div>
          <a href="#" style={{display: 'flex'}}>
              <img src={image} style={{display: "inline-block", width: "2.1875rem", height: "2.1875rem", borderRadius: "50%", aspectRatio: "1", objectFit: "cover"}} />
              <p><strong>{userName}</strong> ⋅ <small>{date}</small></p>
          </a>
        </div>
        <div className="d-flex mb-2" style={{textAlign: 'right'}}>
          <span>
            <button className="btn btn-link text-decoration-none p-0" onClick={handleLike}>
              <i className={liked ? "fa fa-thumbs-up" : "far fa-thumbs-up"} aria-hidden="true"></i>
            </button>{likesCount}
          </span> ⋅ 
          <span>
            <button className="btn btn-link text-decoration-none p-0" onClick={handleDislike}>
              <i className={disliked ? "fa fa-thumbs-down" : "far fa-thumbs-down"} aria-hidden="true"></i>
            </button>{dislikesCount}
          </span>
        </div>

      </div>
      <hr />

      <CommentText comment={comment} />
      
      {replies.length > 0 && s.showReplies 
      ?
      <ul className="list-unstyled">
        {replies.map(reply => (
          <Comment 
          userName={reply.user} 
          comment={reply.comment} 
          date={reply.date} 
          user={user} 
          likesCount={reply.likesCount} 
          liked={reply.liked}
          id={reply.id}
          dislikesCount={reply.dislikesCount}
          disliked={reply.disliked}
          load={load}
          replies={reply.replies}
          key={reply.id}
          image={reply.image}
          />
        ))}
        <button className="btn btn-link text-decoration-none p-0"  onClick={() => setS({...s, showReplies: false})}>Hide Replies</button>

      </ul>

      :
        replies.length > 0 &&
        <button className="btn btn-link text-decoration-none p-0"  onClick={() => setS({...s, showReplies: true})}>Show Replies({replies.length})</button>
      }

      {s.showForm ?
      <>
        <textarea 
          className="form-control" 
          rows="2"
          value={s.text}
          onChange={e => setS({...s, text: e.target.value})}>
        </textarea>
        <button className="btn btn-primary d-flex mt-2" onClick={submitReply}>Submit Reply</button>
        <button className="btn btn-link text-decoration-none p-0" onClick={showRepliesForm}>Close</button>

      </>
      : 
        <button className="btn btn-link text-decoration-none p-0" onClick={showRepliesForm}>Reply</button>
      }
      
    </div>
  );
}

function CommentsList({comments, load}) {
  return (
    <div className="list-group" id="comments-view" style={{margin: '2rem'}} >
      {comments.map(comment => (
        <Comment 
          userName={comment.user}
          date={comment.date}
          comment={comment.comment}
          id={comment.id}
          user={comment.isAuthor}
          likesCount={comment.likesCount}
          liked={comment.liked}
          dislikesCount={comment.dislikesCount}
          disliked={comment.disliked}
          load={load}
          replies={comment.replies}
          key={comment.id}
          image={comment.image}
        />
      ))}
    </div>
  );
}

function App() {
  const [state, setState] = React.useState({
    user: null,
    comments: [],
    currentPage: 1,
    numOfPages: [],
    page: document.getElementById('page').name,
    id: document.getElementById('page').value,
    text: ""
  });

  const handleTextChange = e => {
    setState({
      ...state,
      text: e.target.value
    })
  };

  const handleSubmit = e => {
    e.preventDefault();
    fetch(`/compose/${state.page}`, {
      method: 'POST',
      body: JSON.stringify({
        text: state.text,
        id: state.id
      })
    })
    .then(r => r.json())
    .then(d => {
      console.log(d);
      loadComments();
    })
    .catch(e => {
      console.log(e);
    });
  };

  const loadComments = (page_nr = state.currentPage) => {
    fetch(`/comments/${state.page}/${state.id}/${page_nr}`)
    .then(r => r.json())
    .then(d => {
      setState({
        ...state,
        comments: d.comments,
        numOfPages: d.num,
        currentPage: d.current,
        user: d.user,
        text: '',
      });
      console.log(state.comments);
    })
    .catch(e => {
      console.log(e);
    });
  };
  React.useEffect(() => loadComments(), []);

  return (
    <div style={{marginTop: '2rem', padding: '1rem'}}>
      <AddNewComment 
      handleSubmit={handleSubmit} 
      handleTextChange={handleTextChange} 
      value={state.text} />

      <CommentsList comments={state.comments} load={() => loadComments()}/>
      {state.numOfPages.length > 1 && <nav aria-label="...">
        <ul className="pagination justify-content-center">
          {state.numOfPages.map(p => (
            <li 
              className={p === state.currentPage ? 'page-item active disabled' : 'page-item'} 
              style={{cursor: 'pointer'}}
              onClick={() => {
                loadComments(p);
              }}>
              <span className="page-link">{p}</span>
            </li>
          ))}
        </ul>
      </nav>}
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('comments'));

