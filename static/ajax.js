const getCookie = (name) => {
    if (document.cookie && document.cookie !== '') {
        for (const cookie of document.cookie.split(';')) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) {
                return decodeURIComponent(value);
            }
        }
    }
};
const csrftoken = getCookie('csrftoken');


const Likebutton = async (tweet) => {

    const url = tweet.dataset.url;
    const data = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
    }

    try{
        const response = await fetch(url, data);
        if(!response.ok){
            throw new Error('Response error');
        }
        const tweet_data = await response.json();
        changeStyle(tweet_data, tweet);
    } catch(error){
        console.log(error.message);
    }
}

const changeStyle = (tweet_data, selector) => {
    const count = document.querySelector(`[name="count_${tweet_data.tweet_id}"]`)
    let actionUrl;

    if (tweet_data.is_liked) {
        actionUrl = `/tweets/${tweet_data.tweet_id}/unlike/`
        selector.setAttribute('data-url', actionUrl);
        selector.innerHTML = "いいね解除";
        count.innerHTML = tweet_data.liked_count;
    } else {
        actionUrl = `/tweets/${tweet_data.tweet_id}/like/`
        selector.setAttribute('data-url', actionUrl);
        selector.innerHTML = "いいね";
        count.innerHTML = tweet_data.liked_count;
    }
}
