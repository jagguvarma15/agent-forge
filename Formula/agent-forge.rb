# Homebrew formula for agent-forge.
# This is a reference file. The canonical formula lives in:
#   https://github.com/jagguvarma15/homebrew-agent-forge
#
# To install:
#   brew tap jagguvarma15/agent-forge
#   brew install agent-forge

class AgentForge < Formula
  include Language::Python::Virtualenv

  desc "Generate runnable AI agent projects from markdown specs"
  homepage "https://github.com/jagguvarma15/agent-forge"
  url "https://files.pythonhosted.org/packages/source/a/agent-forge/agent_forge-0.1.0.tar.gz"
  sha256 "PLACEHOLDER_UPDATE_ON_RELEASE"
  license "MIT"

  depends_on "python@3.12"

  resource "anthropic" do
    url "https://files.pythonhosted.org/packages/source/a/anthropic/anthropic-0.39.0.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic/pydantic-2.7.4.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.12.5.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.1.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "questionary" do
    url "https://files.pythonhosted.org/packages/source/q/questionary/questionary-2.0.1.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/source/p/pyyaml/pyyaml-6.0.2.tar.gz"
    sha256 "PLACEHOLDER"
  end

  # Note: Generate accurate sha256 values and complete dependency list using:
  #   pip install homebrew-pypi-poet
  #   poet agent-forge

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "agent-forge", shell_output("#{bin}/agent-forge --version")
  end
end
