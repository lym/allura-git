# -*- coding: utf-8 -*-
"""The application's model objects"""

from .session import ProjectSession
from .neighborhood import Neighborhood, NeighborhoodFile
from .project import Project, ProjectCategory, ProjectFile, AppConfig, SearchConfig, ScheduledMessage
from .discuss import Discussion, Thread, PostHistory, Post, DiscussionAttachment
from .artifact import Artifact, Message, VersionedArtifact, Snapshot, ArtifactLink, Feed, AwardFile, Award, AwardGrant
from .attachments import BaseAttachment
from .auth import User, ProjectRole, OpenId, EmailAddress, ApiToken
from .openid_model import OpenIdStore, OpenIdAssociation, OpenIdNonce
from .filesystem import File
from .tag import TagEvent, Tag, UserTags
from .notification import Notification, Mailbox
from .repository import Repository, RepositoryImplementation, RepoObject, Commit, Tree, Blob
from .repository import CommitReference, LogCache, LastCommitFor, MergeRequest
from .stats import Stats
from .import_batch import ImportBatch
from .oauth import OAuthToken, OAuthConsumerToken, OAuthRequestToken, OAuthAccessToken

from .types import ArtifactReference, ArtifactReferenceType

from .session import main_doc_session, main_orm_session
from .session import project_doc_session, project_orm_session
from .session import artifact_orm_session, repository_orm_session

from ming.orm import MappedClass
MappedClass.compile_all()
