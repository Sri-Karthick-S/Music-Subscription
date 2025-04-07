function subscribeSong(songId, title, artist, album, year, s3_key) {
  const songData = {
    song_id: songId,
    title: title,
    artist: artist,
    album: album,
    year: year,
    s3_key: s3_key
  };

  fetch('/subscribe', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(songData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.message) {
      alert(data.message);
      location.reload();
    } else {
      alert(data.error);
    }
  })
  .catch(error => console.error('Error:', error));
}
