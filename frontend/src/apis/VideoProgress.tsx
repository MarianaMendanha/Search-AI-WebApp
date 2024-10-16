// src/apis/VideoProgress.tsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ProgressBar } from 'react-bootstrap';

interface VideoProgressProps {
  videoName: string;
}

const VideoProgress: React.FC<VideoProgressProps> = ({ videoName }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await axios.get('/api/uploadVideo_status');

        const progressValue = response.data[`video:${videoName}`];

        if (progressValue) {
          const percentage = parseInt(progressValue, 10); // Converte a string para um número
          setProgress(percentage);
        }
      } catch (error) {
        console.error("Error fetching progress:", error);
      }
    };

    const interval = setInterval(fetchProgress, 2000); // Atualiza a cada segundo

    return () => clearInterval(interval); // Limpa o intervalo ao desmontar o componente
  }, [videoName]);

  return (
    <div className="my-3">
      {/* <h5>Upload Progress: {progress}%</h5> */}
      <ProgressBar now={progress} label={`${progress}%`} />
    </div>
  );
};

export default VideoProgress;
