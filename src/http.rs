use futures::future::BoxFuture;
use futures::{AsyncReadExt, FutureExt};
use gpui::http_client::{AsyncBody, HttpClient, Request, Response};
use std::sync::Arc;

#[cfg(feature = "http")]
pub struct SimpleHttpClient {
    client: reqwest::blocking::Client,
    user_agent: gpui::http_client::http::HeaderValue,
}

#[cfg(feature = "http")]
impl SimpleHttpClient {
    pub fn new(user_agent: &str) -> Result<Arc<Self>, reqwest::Error> {
        let client = reqwest::blocking::Client::builder()
            .user_agent(user_agent)
            .build()?;

        let user_agent_header = gpui::http_client::http::HeaderValue::from_str(user_agent)
            .unwrap_or_else(|_| gpui::http_client::http::HeaderValue::from_static("adabraka-ui"));

        Ok(Arc::new(Self {
            client,
            user_agent: user_agent_header,
        }))
    }

    pub fn with_default_user_agent() -> Result<Arc<Self>, reqwest::Error> {
        Self::new("adabraka-ui/0.2.3")
    }
}

#[cfg(feature = "http")]
async fn read_request_body(mut body: AsyncBody) -> gpui::http_client::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    body.read_to_end(&mut bytes)
        .await
        .map_err(|e| gpui::http_client::anyhow!("Failed to read request body: {}", e))?;
    Ok(bytes)
}

#[cfg(feature = "http")]
impl HttpClient for SimpleHttpClient {
    fn type_name(&self) -> &'static str {
        "SimpleHttpClient"
    }

    fn user_agent(&self) -> Option<&gpui::http_client::http::HeaderValue> {
        Some(&self.user_agent)
    }

    fn proxy(&self) -> Option<&gpui::http_client::Url> {
        None
    }

    fn send(
        &self,
        req: Request<AsyncBody>,
    ) -> BoxFuture<'static, gpui::http_client::Result<Response<AsyncBody>>> {
        let client = self.client.clone();
        let (parts, body) = req.into_parts();

        async move {
            let body_bytes = read_request_body(body).await?;
            let method = reqwest::Method::from_bytes(parts.method.as_str().as_bytes())
                .map_err(|e| gpui::http_client::anyhow!("Unsupported HTTP method: {}", e))?;
            let uri_str = parts.uri.to_string();
            let headers: Vec<_> = parts
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect();

            smol::unblock(move || {
                let mut request_builder = client.request(method, &uri_str);

                for (key, value) in headers {
                    request_builder = request_builder.header(key, value);
                }

                if !body_bytes.is_empty() {
                    request_builder = request_builder.body(body_bytes);
                }

                let response = request_builder
                    .send()
                    .map_err(|e| gpui::http_client::anyhow!("HTTP request failed: {}", e))?;

                let status = response.status();
                let headers = response.headers().clone();
                let bytes = response
                    .bytes()
                    .map_err(|e| gpui::http_client::anyhow!("Failed to read response body: {}", e))?;

                let mut builder = gpui::http_client::http::Response::builder().status(
                    gpui::http_client::http::StatusCode::from_u16(status.as_u16())
                        .map_err(|e| gpui::http_client::anyhow!("Invalid status code: {}", e))?,
                );

                for (key, value) in headers.iter() {
                    builder = builder.header(key.as_str(), value.as_bytes());
                }

                let async_body = AsyncBody::from_bytes(bytes::Bytes::from(bytes));
                let response = builder
                    .body(async_body)
                    .map_err(|e| gpui::http_client::anyhow!("Failed to build response: {}", e))?;

                Ok(response)
            })
            .await
        }
        .boxed()
    }
}

pub fn init_http(cx: &mut gpui::App) {
    #[cfg(feature = "http")]
    {
        if let Ok(client) = SimpleHttpClient::with_default_user_agent() {
            cx.set_http_client(client);
        }
    }
    #[cfg(not(feature = "http"))]
    {
        let _ = cx;
    }
}

pub fn init_http_with_user_agent(cx: &mut gpui::App, user_agent: &str) {
    #[cfg(feature = "http")]
    {
        if let Ok(client) = SimpleHttpClient::new(user_agent) {
            cx.set_http_client(client);
        }
    }
    #[cfg(not(feature = "http"))]
    {
        let _ = cx;
        let _ = user_agent;
    }
}
