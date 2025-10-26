import { useRef, useState } from 'react';
import { Button } from './ui/button'
import { Label } from './ui/label';
import { GenerateThumbnailProps } from '@/types';
import { Loader } from 'lucide-react';
import { Input } from './ui/input';
import Image from 'next/image';
import { useToast } from './ui/use-toast';
import { useMutation } from 'convex/react';
import { useUploadFiles } from '@xixixao/uploadstuff/react';
import { api } from '@/convex/_generated/api';

// This component is now solely responsible for uploading a custom thumbnail.
const GenerateThumbnail = ({ 
  setImage, 
  setImageStorageId, 
  image, 
}: GenerateThumbnailProps) => {
// Removed isAiThumbnail state
  const [isImageLoading, setIsImageLoading] = useState(false);
  const imageRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  
  // Convex setup for file upload
  const generateUploadUrl = useMutation(api.files.generateUploadUrl);
  const { startUpload } = useUploadFiles(generateUploadUrl)
  const getImageUrl = useMutation(api.podcasts.getUrl);
  // Removed handleGenerateThumbnail action

  // Unified handler for both generated and uploaded images
  const handleImage = async (blob: Blob, fileName: string) => {
    setIsImageLoading(true);
    setImage('');
    setImageStorageId(null); // Clear storage ID on new attempt

    try {
      // Ensure the blob is correctly treated as a File for uploadstuff
      const file = new File([blob], fileName, { type: blob.type || 'image/jpeg' }); // Use blob type or default

      const uploaded = await startUpload([file]);
      const storageId = (uploaded[0].response as any).storageId;

      setImageStorageId(storageId);

      const imageUrl = await getImageUrl({ storageId });
      setImage(imageUrl!);
      setIsImageLoading(false);
      toast({
        title: "Thumbnail uploaded successfully",
    })
  } catch (error) {
      console.log(error)
      toast({ title: 'Error uploading image', variant: 'destructive'})
      setIsImageLoading(false);
    }
  }


  const uploadImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    
    // Clear previous image on new upload attempt
    setImage('');
    setImageStorageId(null);

    try {
      const files = e.target.files;
      if (!files || files.length === 0) return;

      const file = files[0];
      const blob = await file.arrayBuffer()
        .then((ab) => new Blob([ab], { type: file.type })); // Preserve file type

      handleImage(blob, file.name);
    } catch (error) {
      console.log(error)
      toast({ title: 'Error processing image', variant: 'destructive'})
    }
  }

  return (
    <>
      <div className="flex flex-col gap-5">
        <Label className="text-16 font-bold text-white-1">
          Podcast Thumbnail
        </Label>
        
        {/* Simplified UI: Only Custom Image Upload remains */}
        <div className="image_div" onClick={() => imageRef?.current?.click()}>
          <Input 
            type="file"
            accept="image/*" // Ensure only image files are selectable
            className="hidden"
            ref={imageRef}
            onChange={(e) => uploadImage(e)}
            disabled={isImageLoading}
          />
          {!isImageLoading ? (
            <Image src="/icons/upload-image.svg" width={40} height={40} alt="upload" />
          ): (
            <div className="text-16 flex-center font-medium text-white-1">
              Uploading
              <Loader size={20} className="animate-spin ml-2" />
           </div>
         )}
           <div className="flex flex-col items-center gap-1">
            <h2 className="text-12 font-bold text-orange-1">
              Click to upload
              </h2>
            <p className="text-12 font-normal text-gray-1">SVG, PNG, JPG, or GIF (max. 1080x1080px)</p> 
          </div>
        </div>
      </div>
      {image && (
          <div className="flex-center w-full">
            <Image 
            src={image}
            width={200}
            height={200}
            className="mt-5 object-cover h-52 w-52 rounded-xl"
            alt="thumbnail"
          />
          <Button 
            type="button" 
            onClick={() => {
              setImage('');
              setImageStorageId(null);
            }}
            className="absolute translate-y-[120px] bg-red-500 hover:bg-red-600 text-white-1 py-1 px-3 text-sm"
          >
            Remove
          </Button>
        </div>
      )}
    </>
  )
}

export default GenerateThumbnail










