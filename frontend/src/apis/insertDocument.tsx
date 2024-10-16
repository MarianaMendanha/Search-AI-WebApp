
const insertDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('filename_as_doc_id', 'true');
  
  console.log(file.type);
  // Verifica se o arquivo é um vídeo ou outro tipo
  const isVideo = file.type.startsWith('video/');

  // Define o endpoint com base no tipo de arquivo
  const endpoint = isVideo ? '/api/uploadVideoAsync' : '/api/uploadFile';

  const response = await fetch(endpoint, {
    mode: 'cors',
    method: 'POST',
    body: formData,
  });

  const responseText = await response.text();
  return responseText;
};

export default insertDocument;
