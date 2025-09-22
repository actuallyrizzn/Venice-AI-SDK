#!/usr/bin/env python3
"""
Advanced Image Processing Pipeline

This example demonstrates a complete image processing pipeline including:
- Batch image generation
- Image editing and enhancement
- Style transfer
- Upscaling and optimization
- Error handling and recovery
- Progress tracking
"""

import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from venice_sdk import VeniceClient
from venice_sdk.errors import ImageGenerationError, VeniceAPIError


@dataclass
class ImageProcessingJob:
    """Represents an image processing job."""
    id: str
    prompt: str
    style: Optional[str] = None
    edit_prompt: Optional[str] = None
    upscale_factor: int = 2
    status: str = "pending"
    output_path: Optional[Path] = None
    error: Optional[str] = None


class ImageProcessingPipeline:
    """Advanced image processing pipeline."""
    
    def __init__(self, client: VeniceClient, output_dir: str = "processed_images"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.jobs: List[ImageProcessingJob] = []
        
    def add_job(self, prompt: str, style: Optional[str] = None, 
                edit_prompt: Optional[str] = None, upscale_factor: int = 2) -> str:
        """Add a new image processing job."""
        job_id = f"job_{len(self.jobs) + 1}_{int(time.time())}"
        job = ImageProcessingJob(
            id=job_id,
            prompt=prompt,
            style=style,
            edit_prompt=edit_prompt,
            upscale_factor=upscale_factor
        )
        self.jobs.append(job)
        return job_id
    
    def process_job(self, job: ImageProcessingJob) -> bool:
        """Process a single image job."""
        try:
            print(f"🎨 Processing job {job.id}: {job.prompt[:50]}...")
            job.status = "processing"
            
            # Step 1: Generate base image
            print(f"  📝 Generating base image...")
            generated = self.client.images.generate(
                prompt=job.prompt,
                model="dall-e-3",
                size="1024x1024",
                quality="hd"
            )
            
            base_path = self.output_dir / f"{job.id}_01_generated.png"
            generated.save(base_path)
            print(f"  ✅ Base image saved: {base_path}")
            
            current_image = base_path
            
            # Step 2: Apply style if specified
            if job.style:
                print(f"  🎨 Applying style: {job.style}")
                styled = self.client.image_edit.edit(
                    image=current_image,
                    prompt=f"Apply {job.style} artistic style",
                    model="dall-e-2-edit"
                )
                
                styled_path = self.output_dir / f"{job.id}_02_styled.png"
                styled.save(styled_path)
                current_image = styled_path
                print(f"  ✅ Styled image saved: {styled_path}")
            
            # Step 3: Apply edits if specified
            if job.edit_prompt:
                print(f"  ✏️  Applying edits: {job.edit_prompt}")
                edited = self.client.image_edit.edit(
                    image=current_image,
                    prompt=job.edit_prompt,
                    model="dall-e-2-edit"
                )
                
                edited_path = self.output_dir / f"{job.id}_03_edited.png"
                edited.save(edited_path)
                current_image = edited_path
                print(f"  ✅ Edited image saved: {edited_path}")
            
            # Step 4: Upscale if factor > 1
            if job.upscale_factor > 1:
                print(f"  🔍 Upscaling by {job.upscale_factor}x...")
                upscaled = self.client.image_upscale.upscale(
                    image=current_image,
                    scale=job.upscale_factor,
                    model="real-esrgan"
                )
                
                final_path = self.output_dir / f"{job.id}_04_final.png"
                upscaled.save(final_path)
                current_image = final_path
                print(f"  ✅ Final image saved: {final_path}")
            
            job.output_path = current_image
            job.status = "completed"
            print(f"  🎉 Job {job.id} completed successfully!")
            return True
            
        except ImageGenerationError as e:
            job.status = "failed"
            job.error = f"Image generation error: {e}"
            print(f"  ❌ Job {job.id} failed: {e}")
            return False
        except VeniceAPIError as e:
            job.status = "failed"
            job.error = f"API error: {e}"
            print(f"  ❌ Job {job.id} failed: {e}")
            return False
        except Exception as e:
            job.status = "failed"
            job.error = f"Unexpected error: {e}"
            print(f"  💥 Job {job.id} failed: {e}")
            return False
    
    def process_all_jobs(self, max_concurrent: int = 3) -> Dict[str, Any]:
        """Process all jobs with concurrency control."""
        print(f"🚀 Starting pipeline with {len(self.jobs)} jobs...")
        
        completed = 0
        failed = 0
        
        # Process jobs in batches to respect rate limits
        for i in range(0, len(self.jobs), max_concurrent):
            batch = self.jobs[i:i + max_concurrent]
            print(f"\n📦 Processing batch {i//max_concurrent + 1} ({len(batch)} jobs)")
            
            for job in batch:
                success = self.process_job(job)
                if success:
                    completed += 1
                else:
                    failed += 1
                
                # Small delay between jobs to respect rate limits
                time.sleep(1)
            
            # Longer delay between batches
            if i + max_concurrent < len(self.jobs):
                print("⏳ Waiting before next batch...")
                time.sleep(5)
        
        return {
            "total": len(self.jobs),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / len(self.jobs) if self.jobs else 0
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        job = next((j for j in self.jobs if j.id == job_id), None)
        if not job:
            return None
        
        return {
            "id": job.id,
            "prompt": job.prompt,
            "status": job.status,
            "output_path": str(job.output_path) if job.output_path else None,
            "error": job.error
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get pipeline summary."""
        status_counts = {}
        for job in self.jobs:
            status_counts[job.status] = status_counts.get(job.status, 0) + 1
        
        return {
            "total_jobs": len(self.jobs),
            "status_breakdown": status_counts,
            "output_directory": str(self.output_dir)
        }


def create_sample_jobs(pipeline: ImageProcessingPipeline):
    """Create sample image processing jobs."""
    print("📝 Creating sample jobs...")
    
    # Basic generation jobs
    pipeline.add_job("A serene mountain landscape at sunset")
    pipeline.add_job("A futuristic cyberpunk cityscape at night")
    pipeline.add_job("A peaceful forest with a small cabin")
    
    # Style transfer jobs
    pipeline.add_job(
        "A portrait of a person",
        style="Van Gogh painting style",
        upscale_factor=2
    )
    pipeline.add_job(
        "A landscape scene",
        style="impressionist painting",
        upscale_factor=2
    )
    
    # Complex editing jobs
    pipeline.add_job(
        "A modern office building",
        edit_prompt="Add a rainbow in the sky and make it look more colorful",
        upscale_factor=2
    )
    pipeline.add_job(
        "A simple house",
        style="watercolor painting",
        edit_prompt="Add a garden with flowers in the front yard",
        upscale_factor=4
    )
    
    # High-quality generation
    pipeline.add_job(
        "A detailed architectural drawing of a modern house",
        upscale_factor=2
    )


def demonstrate_batch_processing():
    """Demonstrate batch image processing."""
    print("🎯 Advanced Image Processing Pipeline Demo")
    print("=" * 60)
    
    # Initialize pipeline
    client = VeniceClient()
    pipeline = ImageProcessingPipeline(client, "demo_output")
    
    # Create sample jobs
    create_sample_jobs(pipeline)
    
    # Show initial summary
    summary = pipeline.get_summary()
    print(f"\n📊 Pipeline Summary:")
    print(f"  Total jobs: {summary['total_jobs']}")
    print(f"  Output directory: {summary['output_directory']}")
    
    # Process all jobs
    print(f"\n🚀 Starting processing...")
    start_time = time.time()
    
    results = pipeline.process_all_jobs(max_concurrent=2)
    
    duration = time.time() - start_time
    
    # Show results
    print(f"\n📈 Processing Results:")
    print(f"  Total jobs: {results['total']}")
    print(f"  Completed: {results['completed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Success rate: {results['success_rate']:.1%}")
    print(f"  Total time: {duration:.1f} seconds")
    print(f"  Average time per job: {duration/results['total']:.1f} seconds")
    
    # Show final summary
    final_summary = pipeline.get_summary()
    print(f"\n📊 Final Status Breakdown:")
    for status, count in final_summary['status_breakdown'].items():
        print(f"  {status}: {count}")
    
    # Show completed jobs
    print(f"\n✅ Completed Jobs:")
    for job in pipeline.jobs:
        if job.status == "completed" and job.output_path:
            print(f"  {job.id}: {job.prompt[:50]}... -> {job.output_path}")
        elif job.status == "failed":
            print(f"  {job.id}: FAILED - {job.error}")


def demonstrate_individual_job_processing():
    """Demonstrate individual job processing with monitoring."""
    print("\n🎯 Individual Job Processing Demo")
    print("=" * 50)
    
    client = VeniceClient()
    pipeline = ImageProcessingPipeline(client, "individual_demo")
    
    # Add a complex job
    job_id = pipeline.add_job(
        "A detailed fantasy castle on a mountain peak",
        style="medieval art style",
        edit_prompt="Add dragons flying around the castle and magical lighting",
        upscale_factor=2
    )
    
    print(f"Created job: {job_id}")
    
    # Monitor job status
    def monitor_job():
        while True:
            status = pipeline.get_job_status(job_id)
            if status:
                print(f"Job status: {status['status']}")
                if status['status'] in ['completed', 'failed']:
                    break
            time.sleep(2)
    
    # Process the job
    job = next(j for j in pipeline.jobs if j.id == job_id)
    success = pipeline.process_job(job)
    
    if success:
        print(f"✅ Job completed successfully!")
        print(f"Output: {job.output_path}")
    else:
        print(f"❌ Job failed: {job.error}")


def demonstrate_error_handling():
    """Demonstrate error handling in image processing."""
    print("\n🎯 Error Handling Demo")
    print("=" * 30)
    
    client = VeniceClient()
    pipeline = ImageProcessingPipeline(client, "error_demo")
    
    # Add jobs that might fail
    pipeline.add_job("")  # Empty prompt
    pipeline.add_job("A beautiful image", style="invalid_style")
    pipeline.add_job("A normal image")  # This should work
    
    print("Processing jobs with potential errors...")
    results = pipeline.process_all_jobs()
    
    print(f"\nResults: {results['completed']} completed, {results['failed']} failed")
    
    # Show error details
    for job in pipeline.jobs:
        if job.status == "failed":
            print(f"❌ {job.id}: {job.error}")


def main():
    """Run all image processing examples."""
    try:
        # Main batch processing demo
        demonstrate_batch_processing()
        
        # Individual job processing
        demonstrate_individual_job_processing()
        
        # Error handling demo
        demonstrate_error_handling()
        
        print("\n🎉 All image processing examples completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()
