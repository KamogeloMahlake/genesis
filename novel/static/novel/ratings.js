function RatingField({name, score}) {
    return (
    <h5 className="card-title">
        <span className={score > 0 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 1 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 2 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 3 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 4 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 5 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 6 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 7 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 8 ? 'fa fa-star checked' : 'fa fa-star'}></span>
        <span className={score > 9 ? 'fa fa-star checked' : 'fa fa-star'}></span>
         {score} {name}
      </h5>
    );
}

function Card({ratings, id, set, state}) {
    return (
        <div className="card card-body">
            <div style={{display: "flex", justifyContent: "space-between"}}>
                <div>
                    <RatingField name="Story" score={ratings.story}/>
                    <RatingField name="Writing" score={ratings.writing}/>
                    <RatingField name="World" score={ratings.world}/>
                    <RatingField name="Characters" score={ratings.characters}/>
                </div>
                <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center'}}>
                    <h3 style={{fontSize: '5rem'}}>
                        {ratings.average}
                    </h3>
                    <small>{ratings.count} ratings</small>
                </div>
            </div>

            {!ratings.madeRating && <FormRating id={id} state={state} set={set}/>}
        </div>
    );
}

function FormRating({id, set, state}) {
    const [s, setS] = React.useState({
        story: 5,
        characters: 5,
        world: 5,
        writing: 5,
        open: false
    });

    const story = e => {
        setS({
            ...s,
            story: e.target.value
        });
    };

    const characters = e => {
        setS({
            ...s,
            characters: e.target.value
        });
    };
    const world = e => {
        setS({
            ...s,
            world: e.target.value
        });
    };
    const writing = e => {
        
        setS({
            ...s,
            writing: e.target.value
        });
    };
    const submit = e => {
        e.preventDefault();
        fetch(`/rating/${id}`, {
            method: 'POST', 
            body: JSON.stringify({
                story: s.story,
                characters: s.characters,
                world: s.world,
                writing: s.writing
            })
        })
        .then( r => r.json())
        .then(d => {
            set({
                ...state,
                ratings: d
            })
        })
        .catch(e => console.log(e))
            
}
    const click = e => {
        setS({
            ...s,
            open: !s.open
        })
    }
    return (
        <div>
            <button onClick={click} data-bs-toggle="collapse" href="#form" role="button" aria-expanded="true" aria-controls="form" class="btn" id="rate">{ s.open ? "Close Form" : "Rate Novel"}</button>
            <form onSubmit={submit} id="form" class="card-body collapse" >               
                <div>
                    <label for="id_story">Story Rating(Out of Ten) (Required):</label>
                    <input type="number" name="story" class="form-control" min="1" max="10" required={true} id="id_story" value={s.story} onChange={story}/>
                </div>

                <div>
                    <label for="id_world">World Rating(Out of Ten) (Required):</label>
                    <input type="number" name="world" class="form-control" min="1" max="10" required={true} id="id_world" value={s.world} onChange={world}/>
                </div>

                <div>
                    <label for="id_writing">Writing Rating(Out of Ten) (Required):</label>
                    <input type="number" name="writing" class="form-control" min="1" max="10" required={true} id="id_writing" value={s.writing} onChange={writing}/>
                </div>
                < div>
                    <label for="id_characters">Characters Rating(Out of Ten) (Required):</label>
                    <input type="number" name="characters" class="form-control" min="1" max="10" required={true} id="id_characters" value={s.characters} onChange={characters}/>
                </div>
                <button class="btn btn-primary">Rate</button>
            </form>
        </div>
    )
}
function Rating() {
    const [state, setState] = React.useState({
        id: document.getElementById('page').value,
        ratings: {
            story: 0,
            characters: 0,
            world: 0,
            writing: 0,
            madeRating: false,
            count: 0,
            average: 0
        }
    });
    const getRatings = () => {
        fetch(`/rating/${state.id}`)
        .then(r => r.json())
        .then(d => {
            setState({
                ...state,
                ratings: d
            })
        })
        .catch(e => setState({...state}))
    };

    React.useEffect(() => getRatings(), []);
    return (
        <div>
            <Card  state={state} set={setState} id={state.id} ratings={state.ratings} />
        </div>
    );
}

const rating = ReactDOM.createRoot(document.getElementById('ratings'));

rating.render(
    <React.StrictMode>
        <Rating />
    </React.StrictMode>
);