document.addEventListener("DOMContentLoaded", () => {
    const like_list = document.querySelectorAll('.fa-thumbs-up');
    like_list.forEach(button => {
        button.onclick = () => like_post(button);
        console.log("clicked")
    })

})

const like_post = ( button ) => {
  post_id = button.dataset.postid;
  author_id = button.dataset.authorid;
  console.log(post_id, author_id)
  fetch(`/like/${author_id}/${postid}`)
    .then(response => response.json())
    .then(data => {
      console.log(data.post_likes)
      const thumbs_up = document.querySelector(`#post_num${postid}`);
      thumbs_up.innerHTML = data.post_likes
    })
}
