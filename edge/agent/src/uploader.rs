use crate::{config::S3Config, storage::PendingRecord};
use anyhow::{bail, Context, Result};
use s3::{bucket::Bucket, creds::Credentials, region::Region};
use tokio::fs;

pub struct S3Uploader {
    bucket: Box<Bucket>,
}

impl S3Uploader {
    pub fn new(config: &S3Config) -> Result<Self> {
        let region = Region::Custom {
            region: config.region.clone(),
            endpoint: config.endpoint.clone(),
        };
        let credentials = Credentials::new(
            Some(&config.access_key),
            Some(&config.secret_key),
            None,
            None,
            None,
        )?;
        let mut bucket = Bucket::new(&config.bucket, region, credentials)?;
        if config.path_style {
            bucket = bucket.with_path_style();
        }
        Ok(Self { bucket })
    }

    pub async fn upload(&self, record: &PendingRecord) -> Result<()> {
        let data = fs::read(&record.data_path)
            .await
            .with_context(|| format!("failed to read {}", record.data_path.display()))?;
        let metadata = fs::read(&record.metadata_path)
            .await
            .with_context(|| format!("failed to read {}", record.metadata_path.display()))?;

        self.put(
            &record.metadata.data_object_key,
            &data,
            "application/gzip",
        )
        .await?;
        self.put(
            &record.metadata.metadata_object_key,
            &metadata,
            "application/json",
        )
        .await?;
        Ok(())
    }

    async fn put(&self, key: &str, bytes: &[u8], content_type: &str) -> Result<()> {
        let response = self
            .bucket
            .put_object_with_content_type(key, bytes, content_type)
            .await?;
        let status = response.status_code();
        if !(200..300).contains(&status) {
            bail!("S3 upload for {key} returned HTTP {status}");
        }
        Ok(())
    }
}
